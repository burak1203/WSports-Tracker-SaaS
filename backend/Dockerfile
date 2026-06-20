# 1. İşletim Sistemi ve Python Sürümü (Gereksiz paketleri içermeyen hafif 'slim' versiyon)
FROM python:3.12-slim

# 2. İşletim sistemi içindeki çalışma dizinimizi belirliyoruz
WORKDIR /app

# 3. Önce sadece requirements.txt dosyasını kopyalıyoruz
COPY requirements.txt .

# 4. Bağımlılıkları kur (Gereksiz önbellek dosyalarını tutmadan boyutu küçük tutuyoruz)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Kalan tüm backend kodlarını (main.py, app klasörü vb.) içeri kopyala
COPY . .

# 6. API'nin hangi porttan dışarı açılacağını belirtiyoruz
EXPOSE 8000

# 7. Uygulamayı ayağa kaldıran nihai komut
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]