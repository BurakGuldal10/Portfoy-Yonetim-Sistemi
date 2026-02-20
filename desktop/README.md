# 🖥️ Portföy Yönetim Sistemi - Masaüstü Uygulaması

PyQt6 ile geliştirilen modern ve kullanıcı dostu masaüstü uygulaması.

## 📋 İçindekiler

- [Özellikler](#-özellikler)
- [Sistem Gereksinimleri](#-sistem-gereksinimleri)
- [Kurulum](#-kurulum)
- [Çalıştırma](#-çalıştırma)
- [Mimari](#-mimari)
- [Dosya Yapısı](#-dosya-yapısı)

---

## ✨ Özellikler

### 🔐 Kimlik Doğrulama
- ✅ Kullanıcı kaydı
- ✅ Giriş/Çıkış
- ✅ Token-based authentication (JWT)
- ✅ Otomatik oturum kaydı

### 📊 Dashboard
- ✅ Portföy özeti
- ✅ Toplam yatırım tutarı
- ✅ Toplam komisyon
- ✅ Hisse bazlı detay

### 💼 İşlem Yönetimi
- ✅ İşlem ekleme (Alış/Satış)
- ✅ İşlem silme
- ✅ İşlem güncelleme (planlı)
- ✅ İşlem listesi

### ⚙️ Ayarlar
- ✅ API URL konfigürasyonu
- ✅ Tema seçimi (açık/koyu)
- ✅ Ayarları kaydetme

---

## 💻 Sistem Gereksinimleri

- **Python**: 3.8+
- **İşletim Sistemi**: Windows, macOS, Linux
- **RAM**: 256 MB minimum
- **Disk**: 100 MB
- **Backend API**: http://localhost:8000 (default)

---

## 🚀 Kurulum

### 1. Bağımlılıkları Yükle

```bash
cd desktop
pip install -r requirements.txt
```

### 2. Backend API'yi Başlat

Backend'in çalışıyor olduğundan emin olun:

```bash
# Proje root'unda
uvicorn app.main:app --reload --port 8000
```

---

## ▶️ Çalıştırma

### Windows
```bash
python main.py
```

### macOS/Linux
```bash
python3 main.py
```

### .exe ile (Build edildiyse)
```bash
PortfoyYonetimi.exe
```

---

## 🏗️ Mimari

```
┌─────────────────────────────────────────┐
│      PyQt6 GUI (main_window.py)         │
│  ├─ Dashboard Tab                       │
│  ├─ İşlemler Tab                        │
│  ├─ İşlem Ekle Tab                      │
│  └─ Ayarlar Tab                         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      Auth Window (auth_window.py)       │
│  ├─ Login Tab                           │
│  └─ Register Tab                        │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      API Client (api/client.py)         │
│  ├─ Authentication                      │
│  ├─ Transactions                        │
│  └─ Portfolio                           │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   FastAPI Backend (port 8000)           │
│     (../app/main.py)                    │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│      PostgreSQL Database                │
└─────────────────────────────────────────┘
```

---

## 📁 Dosya Yapısı

```
desktop/
├── main.py                  # Entry point
├── requirements.txt         # Python bağımlılıkları
├── README.md               # Bu dosya
│
└── src/
    ├── app.py              # Ana uygulama sınıfı
    │
    ├── api/
    │   ├── __init__.py
    │   └── client.py       # API HTTP client'ı
    │
    ├── ui/
    │   ├── __init__.py
    │   ├── auth_window.py  # Giriş/Kayıt pencereleri
    │   └── main_window.py  # Ana pencere
    │
    ├── models/
    │   ├── __init__.py
    │   └── data_models.py  # Data class'ları (User, Transaction, vb)
    │
    └── utils/
        ├── __init__.py
        └── session.py      # Oturum ve ayarlar yönetimi
```

---

## 🔗 API Endpoints (Kullanılan)

### Authentication
```
POST   /api/auth/register
POST   /api/auth/login
GET    /api/auth/me
```

### Transactions
```
POST   /api/transactions/
GET    /api/transactions/
GET    /api/transactions/{id}
PUT    /api/transactions/{id}
DELETE /api/transactions/{id}
```

### Portfolio
```
GET    /api/transactions/portfolio/summary
GET    /api/transactions/portfolio/{symbol}
```

---

## 🎨 UI Örneği

### Login Sayfası
```
┌─────────────────────────────────────┐
│ Portföy Yönetim Sistemi            │
│                                     │
│ [Login Tab] [Kayıt Tab]            │
│                                     │
│ E-posta:                           │
│ [____________________________]      │
│                                     │
│ Şifre:                            │
│ [____________________ •••••]       │
│                                     │
│ [Giriş Yap]  [İptal]              │
└─────────────────────────────────────┘
```

### Dashboard
```
┌──────────────────────────────────────────┐
│ Hoşgeldiniz, kullanıcı!  🔄 Yenile 🚪 Çıkış
├──────────────────────────────────────────┤
│ 💰 Toplam Yatırım    💸 Komisyon    📌 Hisse
│ 50,000 TL            250 TL         3
├──────────────────────────────────────────┤
│ Portföy Özeti:
│ ┌────────────────────────────────────────┐
│ │ Hisse  │ Adet │ Ort. Maliyet │ Tutar  │
│ │ THYAO  │ 100  │ 245.50       │ 24550  │
│ │ ASELS  │ 50   │ 52.30        │ 2615   │
│ └────────────────────────────────────────┘
└──────────────────────────────────────────┘
```

---

## 🔧 Sorun Giderme

### API sunucusuna bağlanılamıyor
- Backend'in çalıştığını kontrol edin: `http://localhost:8000/health`
- API URL'sini ayarlarda kontrol edin

### Modüler bulunamadı
Tüm bağımlılıkları yüklediğinizden emin olun:
```bash
pip install -r requirements.txt
```

### İşlem ekleme hatası
- Form alanlarının boş olmadığını kontrol edin
- Hisse kodu formatını kontrol edin (örn: THYAO)

---

## 📈 Gelecek Özellikler

- [ ] İşlem güncelleme
- [ ] Teknik analiz grafikleri
- [ ] PDF rapor oluşturma
- [ ] Email bildirimler
- [ ] Canlı hisse fiyatları
- [ ] Desktop bildirimler
- [ ] Dark mode tema
- [ ] Multi-user desktop sync

---

## 📚 Referanslar

- [PyQt6 Documentation](https://doc.qt.io/qt-6/)
- [Requests Library](https://docs.python-requests.org/)
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html)

---

## 📄 Lisans

MIT License - Detaylar için [LICENSE](../LICENSE) dosyasına bakın.

---

**⭐ Eğer faydalı olmuşsa yıldız verin!**

*Son güncelleme: Şubat 18, 2026*
