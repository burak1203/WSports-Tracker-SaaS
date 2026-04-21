from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.models.models import User
from app.schemas.schemas import UserCreate, UserResponse, UserUpdate
from app.core.security import get_password_hash

# Uç noktaların tamamı Admin rolüyle mühürlendi
router = APIRouter(tags=["Users"], dependencies=[Depends(RoleChecker(["admin"]))])

@router.post("/users/", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Çapraz Kiracı ve İşten Çıkarılma (is_active) Kontrolü
    existing_user = db.query(User).filter(
        User.full_name == user_in.full_name,
        User.company_id == current_user.company_id,
        User.is_active == True # Sadece aktif çalışanlar arasında isim çakışması aranır
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Active user with this name already exists in your company.")

    # GÜVENLİK ZIRHI: company_id kesinlikle dışarıdan alınmaz, token'dan (current_user) damgalanır.
    new_user = User(
        company_id=current_user.company_id,
        full_name=user_in.full_name,
        role=user_in.role,
        password_hash=get_password_hash(user_in.password),
        target_revenue=user_in.target_revenue
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# ==========================================
# KULLANICI LİSTELEME (GET)
# ==========================================
@router.get("/users/", response_model=list[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Sadece kendi şirketindeki aktif çalışanları listele
    return db.query(User).filter(
        User.company_id == current_user.company_id,
        User.is_active == True
    ).order_by(User.id.desc()).offset(skip).limit(limit).all()

# ==========================================
# KULLANICI SİLME (SOFT DELETE)
# ==========================================
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(
        User.id == user_id,
        User.company_id == current_user.company_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot delete yourself.")

    # Veritabanından fiziksel olarak silmiyoruz, geçmiş satış raporları bozulmasın diye pasife çekiyoruz
    user.is_active = False 
    db.commit()
    return None

# USER UPDATE
@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_in.full_name is not None:
        user.full_name = user_in.full_name
    if user_in.role is not None:
        user.role = user_in.role
    if user_in.target_revenue is not None:
        user.target_revenue = user_in.target_revenue
    if user_in.is_active is not None:
        user.is_active = user_in.is_active
    if user_in.password is not None and user_in.password.strip() != "":
        user.password_hash = get_password_hash(user_in.password)

    db.commit()
    db.refresh(user)
    return user