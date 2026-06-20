from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import verify_password, create_access_token
from app.models.models import User, Company
from app.schemas.schemas import Token
import time

router = APIRouter(tags=["Authentication"])

def get_db_for_auth():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/login", response_model=Token)
def login(request: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_for_auth)):
    user = db.query(User).filter(User.full_name == request.username).first()
    
    # 1. Kullanıcı var mı ve şifresi doğru mu?
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 2. GÜVENLİK DUVARI: Kullanıcı silinmişse (pasifse) kapıyı kapat
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user. Your account has been disabled."
        )
    
    # 3. Şirketin lisans durumunu çek
    company = db.query(Company).filter(Company.id == user.company_id).first()
    
    # Eğer license_expires_at doluysa timestamp'e çevir, yoksa sınırsız kabul et (None)
    license_exp_timestamp = int(company.license_expires_at.timestamp()) if company.license_expires_at else None

    # 4. JWT Payload'ını genişlet
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "company_id": user.company_id,
            "role": user.role,
            "license_exp": license_exp_timestamp 
        }
    )
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.full_name,
            "full_name": user.full_name,
            "role": user.role
        }
    }