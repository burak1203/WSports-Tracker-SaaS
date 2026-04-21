from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List
from pydantic import BaseModel

from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.models.models import PercentageRule, User, Activity
from app.schemas.schemas import PercentageRuleResponse # Yeni eklendi

router = APIRouter(tags=["Percentage Rules"], dependencies=[Depends(RoleChecker(["admin"]))])

class RuleAssign(BaseModel):
    activity_id: int
    percentage_rate: Decimal

@router.post("/users/{user_id}/percentage-rules/")
def assign_percentage_rules(
    user_id: int,
    rules: List[RuleAssign],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    target_user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    db.query(PercentageRule).filter(PercentageRule.user_id == target_user.id).delete()

    for rule in rules:
        activity = db.query(Activity).filter(Activity.id == rule.activity_id, Activity.company_id == current_user.company_id).first()
        if activity and activity.is_percentage_eligible:
            new_rule = PercentageRule(
                company_id=current_user.company_id, # 500 HATASINI ÇÖZEN SATIR
                user_id=target_user.id,
                activity_id=activity.id,
                percentage_rate=rule.percentage_rate
            )
            db.add(new_rule)

    db.commit()
    return {"message": "Percentage rules updated successfully."}

# YENİ EKLENEN GET UCU
@router.get("/users/{user_id}/percentage-rules/", response_model=List[PercentageRuleResponse])
def get_percentage_rules(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    target_user = db.query(User).filter(User.id == user_id, User.company_id == current_user.company_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    rules = db.query(PercentageRule).filter(PercentageRule.user_id == target_user.id).all()
    return rules