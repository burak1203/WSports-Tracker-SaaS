from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.models.models import Activity, User
from app.schemas.schemas import ActivityCreate, ActivityResponse, ActivityUpdate

# GLOBAL KALKAN: Bu dosyaya token'sız kimse giremez.
router = APIRouter(tags=["Activities"])

# 1. GET UCU: (İnfocu, Kasa, Yüzdeci, Admin hepsi okuyabilir)
@router.get("/activities/", response_model=List[ActivityResponse], dependencies=[Depends(RoleChecker(["admin", "infocu", "kasa", "yuzdeci"]))])
def get_activities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Activity).filter(
        Activity.company_id == current_user.company_id,
        Activity.is_active == True
    ).all()


# 2. POST UCU: (SADECE ADMIN)
@router.post("/activities/", response_model=ActivityResponse, dependencies=[Depends(RoleChecker(["admin"]))])
def create_activity(
    activity_in: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    existing_activity = db.query(Activity).filter(
        Activity.name == activity_in.name,
        Activity.company_id == current_user.company_id
    ).first()

    if existing_activity:
        raise HTTPException(status_code=400, detail="Activity already exists in your company.")

    new_activity = Activity(
        company_id=current_user.company_id,
        name=activity_in.name,
        is_percentage_eligible=activity_in.is_percentage_eligible
    )

    db.add(new_activity)
    db.commit()
    db.refresh(new_activity)
    return new_activity


# 3. PUT UCU: (SADECE ADMIN)
@router.put("/activities/{activity_id}", response_model=ActivityResponse, dependencies=[Depends(RoleChecker(["admin"]))])
def update_activity(
    activity_id: int,
    activity_in: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    activity = db.query(Activity).filter(Activity.id == activity_id, Activity.company_id == current_user.company_id).first()
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    if activity_in.name is not None:
        activity.name = activity_in.name
    if activity_in.is_percentage_eligible is not None:
        activity.is_percentage_eligible = activity_in.is_percentage_eligible
    if activity_in.is_active is not None:
        activity.is_active = activity_in.is_active

    db.commit()
    db.refresh(activity)
    return activity