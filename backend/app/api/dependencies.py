from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import SessionLocal
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.models import User
import time

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/login")

def get_current_user_token_data(token: str = Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        company_id: int = payload.get("company_id")
        license_exp: int = payload.get("license_exp") # Payload'dan alındı
        
        if user_id is None or company_id is None:
            raise credentials_exception
            
        return {
            "user_id": user_id, 
            "company_id": company_id, 
            "license_exp": license_exp
        }
    except JWTError:
        raise credentials_exception

def get_db(token_data: dict = Depends(get_current_user_token_data)):
    db = SessionLocal()
    try:
        company_id = token_data.get("company_id")
        
        # SQL Injection korumalı PostgreSQL config ayarlaması. 
        # Değişken doğrudan SQL stringine gömülmez, parametre olarak geçilir.
        db.execute(
            text("SELECT set_config('app.current_company_id', :id, true)"),
            {"id": str(company_id)}
        )
        
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def get_current_active_user(
    request: Request, # Hangi endpoint'e (GET, POST) gidildiğini anlamak için Request objesi şart
    token_data: dict = Depends(get_current_user_token_data),
    db: Session = Depends(get_db)
):
    # 1. Abonelik Kontrolü (Token üzerinden DB'ye inmeden)
    license_exp = token_data.get("license_exp")
    
    if license_exp is not None:
        current_time = int(time.time())
        if current_time > license_exp:
            # LİSANS BİTMİŞ! Eğer okuma yapmıyorsa (POST, PUT, DELETE) acımasızca engelle.
            if request.method not in ["GET", "OPTIONS"]:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED, # Ticari hata kodu
                    detail="Subscription expired. System is currently in Read-Only mode."
                )

    # 2. Kullanıcıyı getir
    user = db.query(User).filter(User.id == token_data.get("user_id")).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found or deleted")
        
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles

    # Artık JWT içindeki güvensiz stringe değil, DB'den gelen güncel user nesnesine bakıyor.
    def __call__(self, user: User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for your role"
            )
        return True