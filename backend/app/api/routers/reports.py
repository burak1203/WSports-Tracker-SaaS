import io
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import date
from decimal import Decimal
import pandas as pd
from starlette.concurrency import run_in_threadpool
from typing import List, Dict, Any
from app.models.models import User
from app.api.dependencies import get_db, get_current_active_user, RoleChecker
from app.schemas.schemas import (
    MonthlySummaryResponse, 
    PerformanceSummaryResponse,
    MonthlyReportResponse,
    PerformanceReportResponse,
    DashboardResponse
)

router = APIRouter(tags=["Reports"], dependencies=[Depends(RoleChecker(["admin"]))])

# =========================================================
# CPU-BOUND PANDAS İŞLEMLERİ (TİCARİ MANTIK DÜZELTİLDİ)
# =========================================================
def process_monthly_summary(sales_data: list, expenses_data: list, earnings_data: list) -> list:
    df_sales = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=['currency', 'raw_cash', 'raw_cc', 'exchange_rate'])
    df_exp = pd.DataFrame(expenses_data) if expenses_data else pd.DataFrame(columns=['currency', 'base_expense'])
    df_earn = pd.DataFrame(earnings_data) if earnings_data else pd.DataFrame(columns=['currency', 'base_earn'])

    # 1. Satışları Grupla ve Ana Para Birimine Çevir
    if not df_sales.empty:
        df_sales['base_revenue'] = (df_sales['raw_cash'] + df_sales['raw_cc']) * df_sales['exchange_rate']
        s_grouped = df_sales.groupby('currency').agg(
            raw_cash=('raw_cash', 'sum'),
            raw_cc=('raw_cc', 'sum'),
            base_revenue=('base_revenue', 'sum')
        ).reset_index()
    else:
        s_grouped = pd.DataFrame(columns=['currency', 'raw_cash', 'raw_cc', 'base_revenue'])

    # 2. Gider ve Hakedişleri (Zaten SQL'de çarpılmış halde geliyorlar) Grupla
    e_grouped = df_exp.groupby('currency')['base_expense'].sum().reset_index()
    earn_grouped = df_earn.groupby('currency')['base_earn'].sum().reset_index()

    # 3. OUTER JOIN: Bazı aylarda sadece gider olabilir, satış olmayabilir. Hepsini currency üzerinden bağla.
    merged = pd.merge(s_grouped, e_grouped, on='currency', how='outer')
    merged = pd.merge(merged, earn_grouped, on='currency', how='outer')

    # 4. NaN Temizliği: Olmayan değerleri Decimal(0) yapmazsan sistem çöker
    cols_to_fix = ['raw_cash', 'raw_cc', 'base_revenue', 'base_expense', 'base_earn']
    for col in cols_to_fix:
        if col in merged.columns:
            merged[col] = merged[col].apply(lambda x: Decimal('0.00') if pd.isna(x) else x)

    # 5. NET PROFIT HESABI
    merged['net_profit'] = merged['base_revenue'] - merged['base_earn'] - merged['base_expense']
    
    # Şemadaki isimlerle eşleşmesi için kolon isimlerini düzeltelim
    merged = merged.rename(columns={'base_expense': 'base_expenses', 'base_earn': 'base_earnings'})
    
    return merged.to_dict(orient="records")


def process_performance_summary(sales_data: list, earnings_data: list) -> List[Dict[str, Any]]:
    df_sales = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=['infocu', 'currency', 'raw_sale', 'base_sale'])
    df_earnings = pd.DataFrame(earnings_data) if earnings_data else pd.DataFrame(columns=['infocu', 'currency', 'base_commission'])

    if not df_sales.empty:
        df_sales['raw_sale'] = df_sales['raw_cash'] + df_sales['raw_cc']
        df_sales['base_sale'] = (df_sales['raw_cash'] * df_sales['exchange_rate']) + (df_sales['raw_cc'] * df_sales['exchange_rate'])
        sales_grouped = df_sales.groupby(['infocu', 'currency']).agg(
            raw_sale=('raw_sale', 'sum'),
            base_sale=('base_sale', 'sum')
        ).reset_index()
    else:
        sales_grouped = pd.DataFrame(columns=['infocu', 'currency', 'raw_sale', 'base_sale'])

    if not df_earnings.empty:
        df_earnings['base_commission'] = df_earnings['raw_commission'] * df_earnings['exchange_rate']
        earnings_grouped = df_earnings.groupby(['infocu', 'currency'])['base_commission'].sum().reset_index()
    else:
        earnings_grouped = pd.DataFrame(columns=['infocu', 'currency', 'base_commission'])

    # FLOAT TUZAĞINI ENGELLEMEK: NaN gelirse diye merge'den önce object olarak tuttuğumuzu teyit ediyoruz
    merged_df = pd.merge(sales_grouped, earnings_grouped, on=['infocu', 'currency'], how='outer')
    
    # Fillna yaparken object tiplerini zorlamak
    for col in ['raw_sale', 'base_sale', 'base_commission']:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].apply(lambda x: Decimal('0.00') if pd.isna(x) else x)

    return merged_df.to_dict(orient="records")

def process_dashboard(sales_data: list, expenses_data: list, earnings_data: list) -> dict:
    df_s = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=['date', 'activity_name', 'base_revenue'])
    df_ex = pd.DataFrame(expenses_data) if expenses_data else pd.DataFrame(columns=['base_expense'])
    df_ea = pd.DataFrame(earnings_data) if earnings_data else pd.DataFrame(columns=['base_earn'])

    # 1. Ana Kart Verileri (Total Hesaplamalar)
    tot_rev = df_s['base_revenue'].sum() if not df_s.empty else Decimal('0.00')
    tot_exp = df_ex['base_expense'].sum() if not df_ex.empty else Decimal('0.00')
    tot_earn = df_ea['base_earn'].sum() if not df_ea.empty else Decimal('0.00')
    net_prof = tot_rev - tot_exp - tot_earn

    daily_trend = []
    activity_share = []

    if not df_s.empty:
        # 2. Günlük Trend Çizgi Grafiği İçin Gruplama
        trend_df = df_s.groupby('date')['base_revenue'].sum().reset_index()
        # Tarihe göre sırala
        trend_df = trend_df.sort_values(by='date')
        daily_trend = trend_df.rename(columns={'base_revenue': 'revenue'}).to_dict('records')

        # 3. Aktivite Pasta Grafiği İçin Gruplama
        act_df = df_s.groupby('activity_name')['base_revenue'].sum().reset_index()
        activity_share = act_df.rename(columns={'base_revenue': 'revenue'}).to_dict('records')

    # Float sapmalarına karşı güvenlik çemberi
    return {
        "total_revenue": Decimal(str(tot_rev)) if pd.notna(tot_rev) else Decimal('0.00'),
        "total_expenses": Decimal(str(tot_exp)) if pd.notna(tot_exp) else Decimal('0.00'),
        "total_earnings": Decimal(str(tot_earn)) if pd.notna(tot_earn) else Decimal('0.00'),
        "net_profit": Decimal(str(net_prof)) if pd.notna(net_prof) else Decimal('0.00'),
        "daily_trend": daily_trend,
        "activity_share": activity_share
    }

@router.get("/reports/dashboard", response_model=DashboardResponse)
async def get_dashboard_data(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # YENİ EKLENEN SATIR
):
    # Dashboard SQL sorgularına da "company_id = :cid" eklendi!
    s_query = text("""
        SELECT 
            TO_CHAR(s.created_at, 'YYYY-MM-DD') AS date,
            a.name AS activity_name,
            (s.try_cash + s.try_cc) + 
            ((s.eur_cash + s.eur_cc) * s.eur_rate) + 
            ((s.usd_cash + s.usd_cc) * s.usd_rate) + 
            ((s.gbp_cash + s.gbp_cc) * s.gbp_rate) AS base_revenue
        FROM sales s
        JOIN activities a ON s.activity_id = a.id
        WHERE s.created_at::date >= :s AND s.created_at::date <= :e 
        AND s.is_cancelled = false AND s.status = 'approved' AND s.company_id = :cid
    """)
    
    ex_query = text("""
        SELECT 
            (try_cash + try_cc) + 
            ((eur_cash + eur_cc) * eur_rate) + 
            ((usd_cash + usd_cc) * usd_rate) + 
            ((gbp_cash + gbp_cc) * gbp_rate) AS base_expense
        FROM expenses WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND company_id = :cid
    """)

    ea_query = text("""
        SELECT calculated_amount * exchange_rate AS base_earn
        FROM earnings_log WHERE created_at::date >= :s AND created_at::date <= :e AND company_id = :cid
    """)

    s_rows = db.execute(s_query, {"s": start_date, "e": end_date, "cid": current_user.company_id}).mappings().all()
    ex_rows = db.execute(ex_query, {"s": start_date, "e": end_date, "cid": current_user.company_id}).mappings().all()
    ea_rows = db.execute(ea_query, {"s": start_date, "e": end_date, "cid": current_user.company_id}).mappings().all()

    # CPU-Bound işlemi Threadpool'da çalıştır
    result = await run_in_threadpool(process_dashboard, s_rows, ex_rows, ea_rows)
    
    return result

# =========================================================
# API UÇ NOKTALARI 
# =========================================================

@router.get("/reports/monthly", response_model=MonthlyReportResponse)
async def get_monthly_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user) # YENİ EKLENEN SATIR
):
    # SQL sorgularına "company_id = :cid" filtresi eklendi!
    s_query = text("""
        SELECT 'TRY' as currency, try_cash AS raw_cash, try_cc AS raw_cc, 1.0 AS exchange_rate
        FROM sales WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND status = 'approved' AND company_id = :cid AND (try_cash > 0 OR try_cc > 0)
        UNION ALL
        SELECT 'EUR' as currency, eur_cash AS raw_cash, eur_cc AS raw_cc, eur_rate AS exchange_rate
        FROM sales WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND status = 'approved' AND company_id = :cid AND (eur_cash > 0 OR eur_cc > 0)
        UNION ALL
        SELECT 'USD' as currency, usd_cash AS raw_cash, usd_cc AS raw_cc, usd_rate AS exchange_rate
        FROM sales WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND status = 'approved' AND company_id = :cid AND (usd_cash > 0 OR usd_cc > 0)
        UNION ALL
        SELECT 'GBP' as currency, gbp_cash AS raw_cash, gbp_cc AS raw_cc, gbp_rate AS exchange_rate
        FROM sales WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND status = 'approved' AND company_id = :cid AND (gbp_cash > 0 OR gbp_cc > 0)
    """)
    
    ex_query = text("""
        SELECT 'TRY' as currency, (try_cash + try_cc) AS base_expense FROM expenses WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND company_id = :cid AND (try_cash > 0 OR try_cc > 0)
        UNION ALL
        SELECT 'EUR' as currency, (eur_cash + eur_cc) * eur_rate AS base_expense FROM expenses WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND company_id = :cid AND (eur_cash > 0 OR eur_cc > 0)
        UNION ALL
        SELECT 'USD' as currency, (usd_cash + usd_cc) * usd_rate AS base_expense FROM expenses WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND company_id = :cid AND (usd_cash > 0 OR usd_cc > 0)
        UNION ALL
        SELECT 'GBP' as currency, (gbp_cash + gbp_cc) * gbp_rate AS base_expense FROM expenses WHERE created_at::date >= :s AND created_at::date <= :e AND is_cancelled = false AND company_id = :cid AND (gbp_cash > 0 OR gbp_cc > 0)
    """)

    ea_query = text("""
        SELECT currency, calculated_amount * exchange_rate AS base_earn
        FROM earnings_log WHERE created_at::date >= :s AND created_at::date <= :e
        AND company_id = :cid
    """)

    # current_user.company_id parametre olarak gönderiliyor
    s_rows = db.execute(s_query, {"s": start_date, "e": end_date, "cid": current_user.company_id}).mappings().all()
    ex_rows = db.execute(ex_query, {"s": start_date, "e": end_date, "cid": current_user.company_id}).mappings().all()
    ea_rows = db.execute(ea_query, {"s": start_date, "e": end_date, "cid": current_user.company_id}).mappings().all()

    # CPU-bound (Pandas) işleme - Threadpool'a pasla
    result = await run_in_threadpool(process_monthly_summary, s_rows, ex_rows, ea_rows)
    
    return {"start_date": start_date, "end_date": end_date, "data": result}


@router.get("/reports/performance", response_model=PerformanceReportResponse)
async def get_performance_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    sales_query = text("""
        SELECT u.full_name as infocu, s.currency, s.cash_amount AS raw_cash, s.cc_amount AS raw_cc, s.exchange_rate
        FROM sales s
        JOIN users u ON s.added_by_user_id = u.id
        WHERE s.created_at::date >= :start 
          AND s.created_at::date <= :end 
          AND s.is_cancelled = false
    """)
    
    earnings_query = text("""
        SELECT u.full_name as infocu, e.currency, e.calculated_amount AS raw_commission, e.exchange_rate
        FROM earnings_log e
        JOIN users u ON e.user_id = u.id
        WHERE e.created_at::date >= :start 
          AND e.created_at::date <= :end
    """)

    sales_rows = db.execute(sales_query, {"start": start_date, "end": end_date}).mappings().all()
    earnings_rows = db.execute(earnings_query, {"start": start_date, "end": end_date}).mappings().all()

    result = await run_in_threadpool(process_performance_summary, sales_rows, earnings_rows)
    
    return {"start_date": start_date, "end_date": end_date, "data": result}

# Excel
def generate_monthly_excel(data: list) -> io.BytesIO:
    df = pd.DataFrame(data)
    if not df.empty:
        df['raw_total'] = df['raw_cash'] + df['raw_cc']
        df['base_revenue'] = (df['raw_cash'] * df['exchange_rate']) + (df['raw_cc'] * df['exchange_rate'])
        summary_df = df.groupby('currency').agg(
            raw_cash=('raw_cash', 'sum'),
            raw_cc=('raw_cc', 'sum'),
            base_revenue=('base_revenue', 'sum')
        ).reset_index()
    else:
        summary_df = pd.DataFrame(columns=['currency', 'raw_cash', 'raw_cc', 'base_revenue'])

    buffer = io.BytesIO()
    # Veriyi doğrudan hafızadaki buffer'a Excel formatında yazıyoruz
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        summary_df.to_excel(writer, index=False, sheet_name='Monthly Summary')
    
    buffer.seek(0) # Dosya imlecini başa sarıyoruz ki istemci okuyabilsin
    return buffer


def generate_performance_excel(sales_data: list, earnings_data: list) -> io.BytesIO:
    df_sales = pd.DataFrame(sales_data) if sales_data else pd.DataFrame(columns=['infocu', 'currency', 'raw_sale', 'base_sale'])
    df_earnings = pd.DataFrame(earnings_data) if earnings_data else pd.DataFrame(columns=['infocu', 'currency', 'base_commission'])

    if not df_sales.empty:
        df_sales['raw_sale'] = df_sales['raw_cash'] + df_sales['raw_cc']
        df_sales['base_sale'] = (df_sales['raw_cash'] * df_sales['exchange_rate']) + (df_sales['raw_cc'] * df_sales['exchange_rate'])
        sales_grouped = df_sales.groupby(['infocu', 'currency']).agg(
            raw_sale=('raw_sale', 'sum'),
            base_sale=('base_sale', 'sum')
        ).reset_index()
    else:
        sales_grouped = pd.DataFrame(columns=['infocu', 'currency', 'raw_sale', 'base_sale'])

    if not df_earnings.empty:
        df_earnings['base_commission'] = df_earnings['raw_commission'] * df_earnings['exchange_rate']
        earnings_grouped = df_earnings.groupby(['infocu', 'currency'])['base_commission'].sum().reset_index()
    else:
        earnings_grouped = pd.DataFrame(columns=['infocu', 'currency', 'base_commission'])

    merged_df = pd.merge(sales_grouped, earnings_grouped, on=['infocu', 'currency'], how='outer')
    
    for col in ['raw_sale', 'base_sale', 'base_commission']:
        if col in merged_df.columns:
            merged_df[col] = merged_df[col].apply(lambda x: Decimal('0.00') if pd.isna(x) else x)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        merged_df.to_excel(writer, index=False, sheet_name='Performance Summary')
    
    buffer.seek(0)
    return buffer

# =========================================================
# API UÇ NOKTALARI 
# =========================================================

@router.get("/reports/monthly/export")
async def export_monthly_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    query = text("""
        SELECT currency, cash_amount AS raw_cash, cc_amount AS raw_cc, exchange_rate
        FROM sales 
        WHERE created_at::date >= :start 
          AND created_at::date <= :end 
          AND is_cancelled = false
    """)
    
    rows = db.execute(query, {"start": start_date, "end": end_date}).mappings().all()

    # CPU ve I/O yükünü ana iş parçacığından izole et
    buffer = await run_in_threadpool(generate_monthly_excel, rows)
    
    return StreamingResponse(
        buffer, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=monthly_summary_{start_date}_to_{end_date}.xlsx"}
    )


@router.get("/reports/performance/export")
async def export_performance_summary(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db)
):
    sales_query = text("""
        SELECT u.full_name as infocu, s.currency, s.cash_amount AS raw_cash, s.cc_amount AS raw_cc, s.exchange_rate
        FROM sales s
        JOIN users u ON s.added_by_user_id = u.id
        WHERE s.created_at::date >= :start 
          AND s.created_at::date <= :end 
          AND s.is_cancelled = false
    """)
    
    earnings_query = text("""
        SELECT u.full_name as infocu, e.currency, e.calculated_amount AS raw_commission, e.exchange_rate
        FROM earnings_log e
        JOIN users u ON e.user_id = u.id
        WHERE e.created_at::date >= :start 
          AND e.created_at::date <= :end
    """)

    sales_rows = db.execute(sales_query, {"start": start_date, "end": end_date}).mappings().all()
    earnings_rows = db.execute(earnings_query, {"start": start_date, "end": end_date}).mappings().all()

    buffer = await run_in_threadpool(generate_performance_excel, sales_rows, earnings_rows)
    
    return StreamingResponse(
        buffer, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=performance_summary_{start_date}_to_{end_date}.xlsx"}
    )