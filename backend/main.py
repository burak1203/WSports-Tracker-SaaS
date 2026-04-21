# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.api.routers import auth, sales, reports, users, activities, expenses, percentage_rules
from app.core.config import settings

app = FastAPI(
    title="WSports Tracker SaaS API",
    description="Su sporları işletmeleri için RLS korumalı yönetim sistemi.",
    version="1.0.0"
)

# 1. PERFORMANS: GZip Sıkıştırması
# Minimum 1000 byte üzerindeki yanıtları sıkıştırarak ağ(network) darboğazını engeller.
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 2. GÜVENLİK: Dinamik CORS Koruması
# Sadece .env dosyasında belirtilen domainlerden (Örn: localhost:5173 veya frontend sunucusu) istek kabul eder.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins, 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ların Sisteme Bağlanması
app.include_router(auth.router, prefix="/api/auth")
app.include_router(sales.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(percentage_rules.router, prefix="/api")

@app.get("/")
def root():
    return {"status": "ok", "message": "API is running securely."}