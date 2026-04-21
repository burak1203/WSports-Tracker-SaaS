# backend/Dockerfile
FROM python:3.12-slim

# İşletim sistemi seviyesinde gerekli bağımlılıklar (Postgres driver için)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Önce sadece requirements kopyalanır (Cache optimizasyonu)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm kod kopyalanır
COPY . .

# Üretim (Production) başlatma komutu
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]