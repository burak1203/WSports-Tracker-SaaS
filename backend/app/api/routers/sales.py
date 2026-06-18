from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal

from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.models.models import Sale, User, Activity, PercentageRule, EarningsLog
from app.schemas.schemas import SaleCreate, SaleResponse

router = APIRouter(tags=["Sales"])

# ==========================================
# 1. SATIŞ OLUŞTURMA (Herkes ekleyebilir)
# ==========================================
@router.post("/sales/", response_model=SaleResponse, dependencies=[Depends(RoleChecker(["admin", "kasa", "infocu"]))])
def create_sale(
    sale_in: SaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    activity = db.query(Activity).filter(Activity.id == sale_in.activity_id, Activity.company_id == current_user.company_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Tüm tutarların 0 olup olmadığını kontrol et (Boş satış girilmesin)
    total_input = (
        sale_in.try_cash + sale_in.eur_cash + sale_in.usd_cash + sale_in.gbp_cash +
        sale_in.try_cc + sale_in.eur_cc + sale_in.usd_cc + sale_in.gbp_cc
    )
    if total_input <= 0:
        raise HTTPException(status_code=400, detail="Sale must contain at least one payment amount > 0")

    new_sale = Sale(
        company_id=current_user.company_id,
        activity_id=activity.id,
        # Frontend'den gelen ID varsa onu, yoksa işlemi yapanın kendi ID'sini kullan
        added_by_user_id=sale_in.added_by_user_id if sale_in.added_by_user_id else current_user.id,
        
        try_cash=sale_in.try_cash, eur_cash=sale_in.eur_cash,
        usd_cash=sale_in.usd_cash, gbp_cash=sale_in.gbp_cash,
        
        try_cc=sale_in.try_cc, eur_cc=sale_in.eur_cc,
        usd_cc=sale_in.usd_cc, gbp_cc=sale_in.gbp_cc,
        
        eur_rate=sale_in.eur_rate,
        usd_rate=sale_in.usd_rate,
        gbp_rate=sale_in.gbp_rate,
        
        status="pending"
    )

    db.add(new_sale)
    db.commit()
    db.refresh(new_sale)
    return new_sale


# ==========================================
# 2. SATIŞ ONAYLAMA VE KOMİSYON DAĞITIMI (Sadece Admin ve Kasa)
# ==========================================
@router.put("/sales/{sale_id}/approve", dependencies=[Depends(RoleChecker(["admin", "kasa"]))])
def approve_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.company_id == current_user.company_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending sales can be approved")
    if sale.is_cancelled:
        raise HTTPException(status_code=400, detail="Cancelled sales cannot be approved")

    # Satışı onayla
    sale.status = "approved"

    activity = db.query(Activity).filter(Activity.id == sale.activity_id).first()
    
    # Komisyon kurallarını kontrol et
    if activity and activity.is_percentage_eligible:
        # Kuralları ve kural sahiplerinin rollerini birlikte çekiyoruz
        rules_query = db.query(PercentageRule, User.role).join(User, PercentageRule.user_id == User.id).filter(PercentageRule.activity_id == activity.id).all()
        
        # Satışın içindeki tüm döviz toplamlarını bir listeye alalım
        currencies = [
            ("TRY", (sale.try_cash or 0) + (sale.try_cc or 0), Decimal('1.0')),
            ("EUR", (sale.eur_cash or 0) + (sale.eur_cc or 0), sale.eur_rate),
            ("USD", (sale.usd_cash or 0) + (sale.usd_cc or 0), sale.usd_rate),
            ("GBP", (sale.gbp_cash or 0) + (sale.gbp_cc or 0), sale.gbp_rate)
        ]

        for rule, user_role in rules_query:
            # KOMİSYON FİLTRESİ (MANTIK HATASININ ÇÖZÜMÜ)
            # 1. Kuralın sahibi, satışı yapan kişiyse (infocu kendi satışından pay alır)
            # 2. Kuralın sahibi genel bir 'yuzdeci' ise (satışı kim yaparsa yapsın pay alır)
            if rule.user_id == sale.added_by_user_id or user_role == "yuzdeci":
                
                for curr_name, total_amount, rate in currencies:
                    if total_amount > 0:
                        commission = Decimal(str(total_amount)) * (rule.percentage_rate / Decimal('100.0'))
                        new_earning = EarningsLog(
                            company_id=sale.company_id,
                            user_id=rule.user_id,
                            sale_id=sale.id,
                            currency=curr_name,
                            calculated_amount=commission,
                            exchange_rate=rate,
                            description=f"Otomatik komisyon - {activity.name} (%{rule.percentage_rate})"
                        )
                        db.add(new_earning)

    try:
        db.commit()
        db.refresh(sale)
        return {"message": "Sale approved and commissions distributed successfully", "sale_id": sale.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {str(e)}")

# ==========================================
# 3. SATIŞ LİSTELEME
# ==========================================
@router.get("/sales/", response_model=List[SaleResponse], dependencies=[Depends(RoleChecker(["admin", "kasa", "infocu", "yuzdeci"]))])
def get_sales(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Sale).filter(Sale.company_id == current_user.company_id)

    # İnfocular sadece kendi girdikleri satışları görebilir
    if current_user.role == "infocu":
        query = query.filter(Sale.added_by_user_id == current_user.id)

    return query.order_by(Sale.id.desc()).offset(skip).limit(limit).all()


# ==========================================
# 4. SATIŞ İPTALİ (SOFT DELETE)
# ==========================================
@router.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(RoleChecker(["admin", "kasa"]))])
def cancel_sale(
    sale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.company_id == current_user.company_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
        
    sale.is_cancelled = True
    sale.status = "cancelled"
    
    # İptal edilen satışın hakedişleri de silinir
    db.query(EarningsLog).filter(EarningsLog.sale_id == sale.id).delete()
    
    try:
        db.commit()
        return None
    except Exception as e:
        db.rollback() # Eğer hakedişler silinirken hata çıkarsa satışı iptal etme, geri dön!
        raise HTTPException(status_code=500, detail=f"Database transaction failed: {str(e)}")