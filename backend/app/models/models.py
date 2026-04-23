from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    subdomain = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    license_expires_at = Column(DateTime(timezone=True), nullable=True)

    users = relationship("User", back_populates="company")
    activities = relationship("Activity", back_populates="company")
    sales = relationship("Sale", back_populates="company")
    earnings_logs = relationship("EarningsLog", back_populates="company")
    percentage_rules = relationship("PercentageRule", back_populates="company")
    expenses = relationship("Expense", back_populates="company")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    
    target_revenue = Column(Numeric(12, 2), nullable=True)
    is_target_reached = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True, index=True)

    company = relationship("Company", back_populates="users")
    earnings_logs = relationship("EarningsLog", back_populates="user")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    
    # Drone/GoPro istisnaları için kural
    is_percentage_eligible = Column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="activities")


class PercentageRule(Base):
    __tablename__ = "percentage_rules"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    percentage_rate = Column(Numeric(5, 2), nullable=False)

    company = relationship("Company", back_populates="percentage_rules")
    
    # Bir şirkette, bir aktivite için, aynı kullanıcıya iki farklı kural girilmesini engeller
    __table_args__ = (UniqueConstraint('company_id', 'activity_id', 'user_id', name='_company_activity_user_uc'),)

class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    added_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # NAKİT ÖDEMELER
    try_cash = Column(Numeric(10, 2), default=0)
    eur_cash = Column(Numeric(10, 2), default=0)
    usd_cash = Column(Numeric(10, 2), default=0)
    gbp_cash = Column(Numeric(10, 2), default=0)

    # KREDİ KARTI ÖDEMELERİ
    try_cc = Column(Numeric(10, 2), default=0)
    eur_cc = Column(Numeric(10, 2), default=0)
    usd_cc = Column(Numeric(10, 2), default=0)
    gbp_cc = Column(Numeric(10, 2), default=0)

    # SATIŞ ANINDAKİ KURLAR (Geçmiş raporların bozulmaması için zorunlu)
    eur_rate = Column(Numeric(10, 4), default=1)
    usd_rate = Column(Numeric(10, 4), default=1)
    gbp_rate = Column(Numeric(10, 4), default=1)

    status = Column(String, default="pending") # pending, approved, cancelled
    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    company = relationship("Company", back_populates="sales")
    earnings_logs = relationship("EarningsLog", back_populates="sale")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), index=True)
    added_by_user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String, index=True)
    description = Column(String, nullable=True)

    # NAKİT GİDERLER
    try_cash = Column(Numeric(10, 2), default=0)
    eur_cash = Column(Numeric(10, 2), default=0)
    usd_cash = Column(Numeric(10, 2), default=0)
    gbp_cash = Column(Numeric(10, 2), default=0)

    # KREDİ KARTI GİDERLERİ
    try_cc = Column(Numeric(10, 2), default=0)
    eur_cc = Column(Numeric(10, 2), default=0)
    usd_cc = Column(Numeric(10, 2), default=0)
    gbp_cc = Column(Numeric(10, 2), default=0)

    eur_rate = Column(Numeric(10, 4), default=1)
    usd_rate = Column(Numeric(10, 4), default=1)
    gbp_rate = Column(Numeric(10, 4), default=1)

    is_cancelled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    company = relationship("Company", back_populates="expenses")


class EarningsLog(Base):
    __tablename__ = "earnings_log"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    sale_id = Column(Integer, ForeignKey("sales.id", ondelete="CASCADE"), nullable=True) 
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    
    calculated_amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), nullable=False)
    exchange_rate = Column(Numeric(10, 4), nullable=False, default=1.0000)
    
    description = Column(String) 
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    company = relationship("Company", back_populates="earnings_logs")
    sale = relationship("Sale", back_populates="earnings_logs")
    user = relationship("User", back_populates="earnings_logs")
