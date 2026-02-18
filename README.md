# 📈 Portföy Yönetim Sistemi - Portfolio Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.9+-3776ab?logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Borsa işlemlerinizi yönetin, portföyünüzü analiz edin ve kar/zarar durumunuzu takip edin.

**Manage your stock transactions, analyze your portfolio, and track your profit/loss.**

---

## 📋 İçindekiler (Table of Contents)

- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [API Endpoints](#-api-endpoints)
- [Kurulum](#-kurulum)
- [Testler](#-testler)
- [Dosya Yapısı](#-dosya-yapısı)
- [Katkıda Bulunma](#-katkıda-bulunma)

---

## ✨ Özellikler

### Kimlik Doğrulama & Güvenlik
- ✅ JWT Token tabanlı kimlik doğrulama
- ✅ bcrypt ile şifre hashleme
- ✅ Kullanıcı isolation (her kullanıcı kendi verilerine erişir)
- ✅ Role-based access control (planlı)

### İşlem Yönetimi
- ✅ Alış/Satış işlemlerini ekle, düzenle, sil
- ✅ Hisse koduna göre filtrele
- ✅ Sayfalanmış liste gösterimi
- ✅ İşlem tarihi ve notlar

### Portföy Analizi
- ✅ Ortalama maliyet hesaplama
- ✅ Hisse bazlı portföy özeti
- ✅ Genel portföy özeti
- ✅ Adet ve tutar takibi

### Kod Kalitesi
- ✅ Comprehensive unit tests (23+ test cases)
- ✅ Logging sistemi (file & console)
- ✅ Global exception handlers
- ✅ Input validation (Pydantic)
- ✅ Type hints

---

## 🛠️ Teknoloji Stack

### Backend
| Teknoloji | Versiyon | Kullanım |
|-----------|----------|---------|
| **FastAPI** | 0.115.0 | Web framework |
| **SQLAlchemy** | 2.0.35 | ORM & Database |
| **PostgreSQL** | 15+ | Database |
| **Pydantic** | 2.9.2 | Data validation |
| **python-jose** | 3.3.0 | JWT tokens |
| **passlib** | 1.7.4 | Password hashing |

### Testing
| Teknoloji | Versiyon | Kullanım |
|-----------|----------|---------|
| **pytest** | 7.4.4 | Test framework |
| **httpx** | 0.26.0 | Async HTTP client |

### DevOps
- Git & GitHub (Version control)
- Python venv (Virtual environment)
- Docker (planlı)

---

## 🚀 Hızlı Başlangıç

### Gereksinimleri
- Python 3.9+
- PostgreSQL 12+
- Git

### Kurulum (5 dakika)

1. **Repository'i klonla**
```bash
git clone https://github.com/BurakGuldal10/Portfoy-Yonetim-Sistemi.git
cd Portfoy-Yonetim-Sistemi
```

2. **Virtual environment oluştur**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Bağımlılıkları yükle**
```bash
pip install -r requirements.txt
```

4. **.env dosyası oluştur**
```bash
cp .env.example .env
# .env dosyasını düzenle (veritabanı URL'sini ayarla)
```

5. **Veritabanı tablolarını oluştur** (otomatik olur)
```bash
# Uygulama başladığında tablolar otomatik oluşturulur
```

6. **Uygulamayı çalıştır**
```bash
uvicorn app.main:app --reload --port 8000
```

7. **API'yi test et**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

---

## 📚 API Endpoints

### 🔐 Kimlik Doğrulama (Auth)

```
POST   /api/auth/register          # Yeni kullanıcı kaydı
POST   /api/auth/login             # Giriş yap (JWT token al)
GET    /api/auth/me                # Mevcut kullanıcı bilgisi
```

**Örnek - Kayıt:**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "user123",
    "password": "secure_password",
    "full_name": "Kullanıcı Adı"
  }'
```

**Örnek - Giriş:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secure_password"
```

### 💼 İşlemler (Transactions)

```
POST   /api/transactions/                    # Yeni işlem ekle
GET    /api/transactions/                    # İşlem listesi (sayfalı)
GET    /api/transactions/{id}                # İşlem detayı
PUT    /api/transactions/{id}                # İşlem güncelle
DELETE /api/transactions/{id}                # İşlem sil
```

**Örnek - İşlem Ekle:**
```bash
curl -X POST "http://localhost:8000/api/transactions/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_symbol": "THYAO",
    "stock_name": "Türk Hava Yolları",
    "transaction_type": "BUY",
    "quantity": 100,
    "price_per_unit": 245.50,
    "commission": 12.50,
    "notes": "Uzun vadeli yatırım"
  }'
```

### 📊 Portföy (Portfolio)

```
GET    /api/transactions/portfolio/summary           # Tüm portföy özeti
GET    /api/transactions/portfolio/{stock_symbol}   # Hisse özeti
```

**Örnek - Portföy Özeti:**
```bash
curl -X GET "http://localhost:8000/api/transactions/portfolio/summary" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### ❤️ Sağlık Kontrolü (Health)

```
GET    /                  # Basit health check
GET    /health           # Detaylı sağlık kontrolü (DB bağlantısı)
```

---

## 🧪 Testler

### Testleri Çalıştır

```bash
# Tüm testler
pytest tests/ -v

# Spesifik test dosyası
pytest tests/test_auth.py -v
pytest tests/test_transactions.py -v

# Coverage raporu
pytest tests/ --cov=app --cov-report=html
```

### Test Kapsamı

- **23+ Unit Test Cases**
  - Auth: 10 tests (kayıt, giriş, validasyon)
  - Transactions: 13 tests (CRUD, filtreleme, portföy)
- **Fixtures**: Client, database, test data
- **Coverage**: %90+ kod kapsama

---

## 📁 Dosya Yapısı

```
Portfoy-Yonetim-Sistemi/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI uygulaması
│   ├── config.py               # Konfigürasyon ayarları
│   ├── database.py             # Veritabanı bağlantısı
│   ├── logger.py               # Logging sistemi
│   ├── security.py             # JWT & password hashing
│   │
│   ├── models/                 # SQLAlchemy ORM modelleri
│   │   ├── user.py
│   │   └── transaction.py
│   │
│   ├── schemas/                # Pydantic validation schemas
│   │   ├── user.py
│   │   └── transaction.py
│   │
│   ├── routers/                # API endpoints
│   │   ├── auth.py
│   │   └── transaction.py
│   │
│   └── services/               # İş mantığı (Business logic)
│       ├── auth_service.py
│       └── portfolio_service.py
│
├── tests/
│   ├── conftest.py            # SQL fixtures
│   ├── test_auth.py           # Auth testleri
│   └── test_transactions.py   # Transaction testleri
│
├── logs/                       # Uygulama logları
│   ├── app.log
│   └── errors.log
│
├── requirements.txt           # Python bağımlılıkları
├── pytest.ini                 # Pytest konfigürasyonu
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
└── README.md                  # Bu dosya
```

---

## ⚙️ Konfigürasyon

### .env Dosyası

```env
# Veritabanı
DATABASE_URL=postgresql://user:password@localhost:5432/finans_takip

# JWT
SECRET_KEY=your-secret-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Ortam
ENVIRONMENT=development
```

### Production Ayarları

```env
ENVIRONMENT=production
DATABASE_URL=postgresql://prod_user:strong_pwd@prod_host:5432/db
SECRET_KEY=$(openssl rand -hex 32)  # Güçlü random key
ALLOWED_ORIGINS=https://app.example.com
```

---

## 🔒 Güvenlik Özellikleri

- ✅ **Password Security**: bcrypt hashing
- ✅ **JWT Tokens**: 30 dakikalık süre, secret key koruması
- ✅ **User Isolation**: Her kullanıcı kendi verilerine erişir
- ✅ **Input Validation**: Pydantic ile tüm girdiler kontrol edilir
- ✅ **CORS**: Belirtilen originler'e izin ver
- ✅ **Logging**: Tüm önemli aktiviteler kaydedilir
- ✅ **Error Handling**: Bilgi sızıntısı yok

---

## 📈 Gelecek Özellikler (Roadmap)

- [ ] Canlı hisse fiyat verileri (API integrasyon)
- [ ] Teknik analiz göstergeleri (RSI, MACD, vb)
- [ ] Portföy raporları (PDF export)
- [ ] Bildirimler (SMS, Email)
- [ ] Mobile app (Flutter)
- [ ] Docker & Kubernetes deployment
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Multi-language support (EN, TR, vb)

---

## 🐛 Sorun Bildirme

Bir sorun bulduğunuz mu? Lütfen [Issues](https://github.com/BurakGuldal10/Portfoy-Yonetim-Sistemi/issues) sayfasında bildir.

---

## 🤝 Katkıda Bulunma

Projeye katkı vermek isterseniz:

1. **Fork** et
2. **Feature branch** oluştur (`git checkout -b feature/AmazingFeature`)
3. **Commit** et (`git commit -m 'Add some AmazingFeature'`)
4. **Push** et (`git push origin feature/AmazingFeature`)
5. **Pull Request** aç

---

## 📄 Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Bkz. [LICENSE](LICENSE) dosyası detaylar için.

---

## 👤 Geliştirici

**Burak Yılmaz**
- GitHub: [Portfoy-Yonetim-Sistemi](https://github.com/BurakGuldal10/Portfoy-Yonetim-Sistemi)

---

## 📞 Destek & İletişim

Sorularınız ve geri bildiriminiz için lütfen aşağıdaki kanalları kullanın:

- 🐛 **Bug Raporları**: [GitHub Issues](https://github.com/BurakGuldal10/Portfoy-Yonetim-Sistemi/issues)
- 💬 **Özellik İstekleri**: [GitHub Discussions](https://github.com/BurakGuldal10/Portfoy-Yonetim-Sistemi/discussions)
- ⭐ **Proje Desteği**: Repository'ye yıldız verin

**Not**: Direct email iletişimi için lütfen GitHub Issues üzerinden iletişime geçin.

---

## 🙏 Teşekkürler

- FastAPI documentation
- SQLAlchemy ORM
- Pytest testing framework
- Python community

---

**⭐ Eğer projeyi beğendiyseniz, lütfen yıldız verin!**

---

*Son güncelleme: Şubat 18, 2026*