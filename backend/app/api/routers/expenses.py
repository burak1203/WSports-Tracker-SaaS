from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal

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
    # Toplam tutar kontrolü
    if expense_in.cash_amount + expense_in.cc_amount <= 0:
        raise HTTPException(status_code=400, detail="Expense amount must be greater than zero.")

    # Temsili kur çekimi (Canlıda bir kur servisine bağlanabilir)
    current_exchange_rate = Decimal('1.0000')

    new_expense = Expense(
        company_id=current_user.company_id,
        added_by_user_id=current_user.id,
        category=expense_in.category,
        cash_amount=expense_in.cash_amount,
        cc_amount=expense_in.cc_amount,
        currency=expense_in.currency,
        exchange_rate=current_exchange_rate,
        description=expense_in.description
    )

    db.add(new_expense)
    db.commit()
    db.refresh(new_expense)
    return new_expense

@router.get("/expenses/", response_model=list[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # RLS burada otomatik devrededir, sadece şirketin giderleri döner
    return db.query(Expense).filter(Expense.is_cancelled == False).order_by(Expense.created_at.desc()).all()