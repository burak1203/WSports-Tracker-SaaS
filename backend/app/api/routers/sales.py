from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from typing import List

from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.models.models import User, Sale, Activity, PercentageRule, EarningsLog
from app.schemas.schemas import SaleCreate, SaleResponse, SaleListResponse, EarningsListResponse

router = APIRouter(tags=["Sales"])

# ==========================================
# 1. REZERVASYON OLUŞTURMA (INFOCU & ADMIN)
# ==========================================
@router.post("/sales/", response_model=SaleResponse, dependencies=[Depends(RoleChecker(["infocu", "admin", "kasa"]))])
def create_sale(
    sale_data: SaleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    total_amount = sale_data.cash_amount + sale_data.cc_amount
    if total_amount <= 0:
        raise HTTPException(status_code=400, detail="Total amount must be greater than zero.")

    current_exchange_rate = Decimal('1.0000') # Dış servisten geldiği varsayılır

    activity = db.query(Activity).filter(Activity.id == sale_data.activity_id).first()
    if not activity or not activity.is_active:
        raise HTTPException(status_code=404, detail="Activity not found or inactive.")

    # Sadece PENDING olarak kaydet. Komisyon yok, Bonus yok.
    new_sale = Sale(
        company_id=current_user.company_id,
        added_by_user_id=current_user.id,
        activity_id=activity.id,
        cash_amount=sale_data.cash_amount,
        cc_amount=sale_data.cc_amount,
        currency=sale_data.currency,
        exchange_rate=current_exchange_rate,
        status="pending" # STATÜ BEKLEMEDE
    )
    db.add(new_sale)
    db.commit()
    
    return {"id": new_sale.id, "message": "Reservation created and waiting for approval.", "status": "pending"}


# ==========================================
# 2. ONAY MEKANİZMASI VE KOMİSYON DAĞITIMI (SADECE ADMIN VE KASA)
# ==========================================
@router.put("/sales/{sale_id}/approve", response_model=SaleResponse, dependencies=[Depends(RoleChecker(["admin", "kasa"]))])
def approve_sale(
    sale_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    # 1. Çift Tıklama (Race Condition) Engellemesi: FOR UPDATE kilitli çekim
    sale = db.query(Sale).filter(
        Sale.id == sale_id,
        Sale.company_id == current_user.company_id
    ).with_for_update().first()

    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found.")
    
    if sale.status != "pending":
        raise HTTPException(status_code=400, detail=f"This sale cannot be approved. Current status: {sale.status}")

    # 2. Statüyü güncelle
    sale.status = "approved"
    total_amount = sale.cash_amount + sale.cc_amount

    # 3. Komisyon Dağıtımı (Kilitli Kur Üzerinden)
    activity = db.query(Activity).filter(Activity.id == sale.activity_id).first()
    
    if activity and activity.is_percentage_eligible:
        rules = db.query(PercentageRule).filter(PercentageRule.activity_id == activity.id).all()
        for rule in rules:
            calculated_cut = (total_amount * rule.percentage_rate) / Decimal('100.00')
            earning = EarningsLog(
                company_id=current_user.company_id,
                sale_id=sale.id,
                user_id=rule.user_id,
                calculated_amount=calculated_cut,
                currency=sale.currency,
                exchange_rate=sale.exchange_rate, # Anlaşılan kur korundu
                description=f"Auto Commission - {activity.name} ({rule.percentage_rate}%)"
            )
            db.add(earning)

    # 4. Kota Kontrolü ve Bonus (Satışı giren infocu için hedefe bakılır)
    infocu_user = db.query(User).filter(User.id == sale.added_by_user_id).with_for_update().first()
    
    if infocu_user and infocu_user.target_revenue and not infocu_user.is_target_reached:
        # PENDING olanlar değil, sadece APPROVED olan iptal edilmemiş satışlar hedefe sayılır
        total_revenue_result = db.query(func.sum(Sale.cash_amount + Sale.cc_amount)).filter(
            Sale.added_by_user_id == infocu_user.id,
            Sale.is_cancelled == False,
            Sale.status == "approved"
        ).scalar()
        
        current_cumulative = total_revenue_result or Decimal('0.00')
        
        if current_cumulative >= infocu_user.target_revenue:
            infocu_user.is_target_reached = True
            bonus_earning = EarningsLog(
                company_id=infocu_user.company_id,
                sale_id=sale.id,
                user_id=infocu_user.id,
                calculated_amount=Decimal('2000.00'),
                currency=sale.currency,
                exchange_rate=sale.exchange_rate,
                description="Target Revenue Bonus Reached"
            )
            db.add(bonus_earning)

    db.commit()
    return {"id": sale.id, "message": "Sale approved and commissions distributed.", "status": sale.status}


# ==========================================
# 3. GET İŞLEMLERİ 
# ==========================================
@router.get("/sales/", response_model=List[SaleListResponse], dependencies=[Depends(RoleChecker(["infocu", "admin", "kasa"]))])
def get_sales(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status_filter: str = Query(None, description="Filter by status: pending, approved, cancelled"),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Sale)

    # Parametre ile filtreleme imkanı (Frontend'de "Bekleyenler" tablosu için)
    if status_filter:
        query = query.filter(Sale.status == status_filter)

    if current_user.role == "infocu":
        query = query.filter(Sale.added_by_user_id == current_user.id)
    
    sales = query.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()
    return sales


@router.get("/earnings/", response_model=List[EarningsListResponse], dependencies=[Depends(RoleChecker(["infocu", "admin", "kasa", "yuzdeci"]))])
def get_earnings(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(EarningsLog)

    if current_user.role in ["infocu", "yuzdeci"]:
        query = query.filter(EarningsLog.user_id == current_user.id)
        
    earnings = query.order_by(EarningsLog.created_at.desc()).offset(skip).limit(limit).all()
    return earnings