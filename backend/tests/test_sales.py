import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool # EKLENEN YENİ İMPORT

from main import app
from app.core.database import Base
from app.api.dependencies import get_db, get_current_active_user
from app.models.models import User, Activity, Sale, PercentageRule, EarningsLog, Company

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class MockAdminUser:
    id = 1
    role = "admin"
    company_id = 1
    target_revenue = 0

app.dependency_overrides[get_current_active_user] = lambda: MockAdminUser()

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    # 1. Şirket (Foreign Key hatalarını önlemek için SQL'deki gibi 1 numaralı şirketi yaratıyoruz)
    company = Company(id=1, name="Yılmaz Su Sporları", subdomain="yilmaz_su_sporlari", is_active=True)
    db.add(company)
    db.commit()

    # 2. Kullanıcılar (SQL Şemasına tam uyumlu: email YOK, password_hash VAR)
    user_ayse = User(id=2, full_name="Ayse", role="infocu", company_id=1, password_hash="123", is_active=True)
    user_mehmet = User(id=3, full_name="Mehmet", role="infocu", company_id=1, password_hash="123", is_active=True)
    db.add_all([user_ayse, user_mehmet])
    db.commit()

    # 3. Aktivite
    activity = Activity(id=1, name="Jetski", company_id=1, is_active=True, is_percentage_eligible=True)
    db.add(activity)
    db.commit()

    # 4. Komisyon Kuralları
    rule1 = PercentageRule(activity_id=1, user_id=2, company_id=1, percentage_rate=10.0)
    rule2 = PercentageRule(activity_id=1, user_id=3, company_id=1, percentage_rate=10.0)
    db.add_all([rule1, rule2])
    db.commit()

    # 5. Satış (SQL'e uygun varsayılan kur değerleriyle)
    sale = Sale(
        id=1, company_id=1, activity_id=1, added_by_user_id=2,
        try_cash=1000.0, eur_cash=0, usd_cash=0, gbp_cash=0,
        try_cc=0, eur_cc=0, usd_cc=0, gbp_cc=0,
        eur_rate=35.0, usd_rate=32.0, gbp_rate=40.0,
        status="pending", is_cancelled=False
    )
    db.add(sale)
    db.commit()
    db.close()

    yield 

    Base.metadata.drop_all(bind=engine)


def test_approve_sale_commission_distribution():
    # Admin olarak satışı onaylama isteği atıyoruz
    response = client.put("/api/sales/1/approve")
    
    assert response.status_code == 200

    db = TestingSessionLocal()
    earnings = db.query(EarningsLog).filter(EarningsLog.sale_id == 1).all()
    
    # Beklenti 1: Sadece 1 adet komisyon kaydı oluşmalı (Ayşe için), Mehmet'e gitmemeli
    assert len(earnings) == 1
    
    # Beklenti 2: Oluşan komisyonun sahibi Ayşe (user_id=2) olmalı
    assert earnings[0].user_id == 2
    
    # Beklenti 3: 1000 TL'nin %10'u 100 TL olarak hesaplanmış olmalı
    assert float(earnings[0].calculated_amount) == 100.0
    
    db.close()