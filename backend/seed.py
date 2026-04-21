from app.core.database import SessionLocal
from app.models.models import Company, User, Activity, PercentageRule
from app.core.security import get_password_hash
from decimal import Decimal

def seed_database():
    db = SessionLocal()
    try:
        # 1. Şirket Kontrolü (Varsa ekleme)
        company = db.query(Company).filter(Company.subdomain == "yilmaz_su_sporlari").first()
        if not company:
            company = Company(
                name="Yılmaz Su Sporları",
                subdomain="yilmaz_su_sporlari",
                is_active=True
            )
            db.add(company)
            db.flush() # ID almak için flush
            print(f"Şirket oluşturuldu: {company.name} (ID: {company.id})")

        # 2. Kullanıcıları Oluşturma
        admin_user = db.query(User).filter(User.full_name == "admin_yilmaz").first()
        if not admin_user:
            admin_user = User(
                company_id=company.id,
                full_name="admin_yilmaz",
                role="admin",
                password_hash=get_password_hash("123456") # Basit test şifresi
            )
            db.add(admin_user)

        infocu_user = db.query(User).filter(User.full_name == "infocu_ali").first()
        if not infocu_user:
            infocu_user = User(
                company_id=company.id,
                full_name="infocu_ali",
                role="infocu",
                password_hash=get_password_hash("123456"),
                target_revenue=Decimal('50000.00') # 50.000 TL barajı
            )
            db.add(infocu_user)
            db.flush()
            print(f"Kullanıcılar oluşturuldu. İnfocu ID: {infocu_user.id}")

        # 3. Aktiviteleri Oluşturma
        jetski = db.query(Activity).filter(Activity.name == "Jetski", Activity.company_id == company.id).first()
        if not jetski:
            jetski = Activity(
                company_id=company.id,
                name="Jetski",
                is_percentage_eligible=True # Komisyon verilir
            )
            db.add(jetski)

        drone = db.query(Activity).filter(Activity.name == "Drone Çekimi", Activity.company_id == company.id).first()
        if not drone:
            drone = Activity(
                company_id=company.id,
                name="Drone Çekimi",
                is_percentage_eligible=False # İstisna: Komisyon verilmez
            )
            db.add(drone)
            db.flush()
            print("Aktiviteler oluşturuldu.")

        # 4. Yüzde Kuralını Oluşturma (Ali, Jetski'den %10 alır)
        rule = db.query(PercentageRule).filter(
            PercentageRule.user_id == infocu_user.id, 
            PercentageRule.activity_id == jetski.id
        ).first()
        
        if not rule:
            rule = PercentageRule(
                company_id=company.id,
                activity_id=jetski.id,
                user_id=infocu_user.id,
                percentage_rate=Decimal('10.00')
            )
            db.add(rule)
            print("Kural oluşturuldu.")

        db.commit()
        print("--- Veritabanı başarıyla tohumlandı! ---")

    except Exception as e:
        db.rollback()
        print(f"Hata oluştu: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()