from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, List, Literal
from datetime import datetime, date

class MonthlySummaryResponse(BaseModel):
    currency: str
    raw_cash: Decimal
    raw_cc: Decimal
    base_revenue: Decimal   # Brüt Ciro (Kurla çarpılmış)
    base_expenses: Decimal  # Toplam Gider (Kurla çarpılmış) - YENİ
    base_earnings: Decimal  # Ödenen Komisyon (Kurla çarpılmış) - YENİ
    net_profit: Decimal     # NET KÂR (Revenue - Expenses - Earnings) - YENİ

class PerformanceSummaryResponse(BaseModel):
    infocu: str
    currency: str
    raw_sale: Decimal
    base_sale: Decimal
    base_commission: Decimal

class MonthlyReportResponse(BaseModel):
    start_date: date
    end_date: date
    data: List[MonthlySummaryResponse]

class PerformanceReportResponse(BaseModel):
    start_date: date
    end_date: date
    data: List[PerformanceSummaryResponse]

class UserInfo(BaseModel):
    id: int
    username: str
    full_name: str
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserInfo  # Frontend'in beklediği kullanıcı bilgisi eklendi

class SaleCreate(BaseModel):
    activity_id: int
    added_by_user_id: Optional[int] = None  # Frontend'den gelen infocu ID'si (Opsiyonel)
    
    try_cash: Optional[Decimal] = Decimal('0.00')
    eur_cash: Optional[Decimal] = Decimal('0.00')
    usd_cash: Optional[Decimal] = Decimal('0.00')
    gbp_cash: Optional[Decimal] = Decimal('0.00')
    
    try_cc: Optional[Decimal] = Decimal('0.00')
    eur_cc: Optional[Decimal] = Decimal('0.00')
    usd_cc: Optional[Decimal] = Decimal('0.00')
    gbp_cc: Optional[Decimal] = Decimal('0.00')

    eur_rate: Decimal
    usd_rate: Decimal
    gbp_rate: Decimal

class ExpenseCreate(BaseModel):
    category: str
    description: Optional[str] = None
    
    try_cash: Optional[Decimal] = Decimal('0.00')
    eur_cash: Optional[Decimal] = Decimal('0.00')
    usd_cash: Optional[Decimal] = Decimal('0.00')
    gbp_cash: Optional[Decimal] = Decimal('0.00')
    
    try_cc: Optional[Decimal] = Decimal('0.00')
    eur_cc: Optional[Decimal] = Decimal('0.00')
    usd_cc: Optional[Decimal] = Decimal('0.00')
    gbp_cc: Optional[Decimal] = Decimal('0.00')

    eur_rate: Decimal
    usd_rate: Decimal
    gbp_rate: Decimal

class SaleResponse(BaseModel):
    id: int
    company_id: int
    activity_id: int
    added_by_user_id: int
    status: str
    is_cancelled: bool

    try_cash: Decimal
    eur_cash: Decimal
    usd_cash: Decimal
    gbp_cash: Decimal
    try_cc: Decimal
    eur_cc: Decimal
    usd_cc: Decimal
    gbp_cc: Decimal
    eur_rate: Decimal
    usd_rate: Decimal
    gbp_rate: Decimal

# Eksik olan ve sunucuyu çökerten şemalar:
class SaleListResponse(BaseModel):
    id: int
    activity_id: int
    added_by_user_id: int
    cash_amount: Decimal
    cc_amount: Decimal
    currency: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class EarningsListResponse(BaseModel):
    id: int
    sale_id: Optional[int]
    user_id: int
    calculated_amount: Decimal
    currency: str
    description: str
    created_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    full_name: str
    # Literal sayesinde bu 4 değer dışında bir metin gelirse Pydantic 422 hatası fırlatır ve sistemi korur.
    role: Literal["admin", "infocu", "kasa", "yuzdeci"] 
    password: str
    target_revenue: Optional[Decimal] = None

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[Literal["admin", "infocu", "kasa", "yuzdeci"]] = None
    password: Optional[str] = None
    target_revenue: Optional[Decimal] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    full_name: str
    role: str
    company_id: int
    is_target_reached: bool
    is_active: bool

    class Config:
        from_attributes = True

class ActivityCreate(BaseModel):
    name: str
    is_percentage_eligible: bool

class ActivityUpdate(BaseModel):
    name: Optional[str] = None
    is_percentage_eligible: Optional[bool] = None
    is_active: Optional[bool] = None

class ActivityResponse(BaseModel):
    id: int
    name: str
    is_percentage_eligible: bool
    is_active: bool
    company_id: int

    class Config:
        from_attributes = True

class ExpenseResponse(BaseModel):
    id: int
    category: str
    exchange_rate: Decimal
    description: Optional[str]
    is_cancelled: bool
    created_at: datetime

    try_cash: Decimal
    eur_cash: Decimal
    usd_cash: Decimal
    gbp_cash: Decimal
    try_cc: Decimal
    eur_cc: Decimal
    usd_cc: Decimal
    gbp_cc: Decimal
    eur_rate: Decimal
    usd_rate: Decimal
    gbp_rate: Decimal

    class Config:
        from_attributes = True

class PercentageRuleResponse(BaseModel):
    id: int
    user_id: int
    activity_id: int
    percentage_rate: Decimal
    
    class Config:
        from_attributes = True

class DailyTrend(BaseModel):
    date: str
    revenue: Decimal

class ActivityShare(BaseModel):
    activity_name: str
    revenue: Decimal

class DashboardResponse(BaseModel):
    total_revenue: Decimal
    total_expenses: Decimal
    total_earnings: Decimal
    net_profit: Decimal
    daily_trend: List[DailyTrend]
    activity_share: List[ActivityShare]