from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.routers import auth, users, activities, sales, reports, expenses, percentage_rules

app = FastAPI(title="WSports Tracker API", version="1.0.0")

# GÜVENLİK: Sadece kendi frontend'imizden gelen isteklere izin ver
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # "*" yerine kısıtlı liste
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Hata Yakalayıcı (Ham hataları gizle)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Sunucu tarafında beklenmedik bir hata oluştu. Lütfen sistem yöneticisine danışın."},
    )

# Rotalar
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(activities.router, prefix="/api")
app.include_router(sales.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(expenses.router, prefix="/api")
app.include_router(percentage_rules.router, prefix="/api")