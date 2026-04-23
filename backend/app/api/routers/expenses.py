from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.models.models import Expense, User
from app.schemas.schemas import ExpenseCreate, ExpenseResponse

router = APIRouter(tags=["Expenses"], dependencies=[Depends(RoleChecker(["admin", "kasa"]))])

@router.post("/expenses/", response_model=ExpenseResponse)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    new_expense = Expense(
        company_id=current_user.company_id,
        added_by_user_id=current_user.id,
        category=expense_in.category,
        description=expense_in.description,
        
        try_cash=expense_in.try_cash, eur_cash=expense_in.eur_cash,
        usd_cash=expense_in.usd_cash, gbp_cash=expense_in.gbp_cash,
        
        try_cc=expense_in.try_cc, eur_cc=expense_in.eur_cc,
        usd_cc=expense_in.usd_cc, gbp_cc=expense_in.gbp_cc,
        
        eur_rate=expense_in.eur_rate, usd_rate=expense_in.usd_rate, gbp_rate=expense_in.gbp_rate
    )
    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses/", response_model=List[ExpenseResponse])
def get_expenses(
    skip: int = 0, limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return db.query(Expense).filter(
        Expense.company_id == current_user.company_id, 
        Expense.is_cancelled == False
    ).order_by(Expense.id.desc()).offset(skip).limit(limit).all()

@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.company_id == current_user.company_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
        
    expense.is_cancelled = True
    db.commit()
    return None