"""
API Test Betiği
================
Tüm endpointleri sırasıyla test eder.
"""
import requests
import json

BASE = "http://localhost:8000/api"
HEADERS = {}


def print_response(title, resp):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")
    print(f"Status: {resp.status_code}")
    try:
        print(json.dumps(resp.json(), indent=2, ensure_ascii=False))
    except Exception:
        print(resp.text)


# 1. Kullanici kaydi
resp = requests.post(f"{BASE}/auth/register", json={
    "email": "buraq@gmail.com",
    "username": "buraq",
    "password": "test123456",
    "full_name": "Burak Yilmaz"
})
print_response("1. KULLANICI KAYDI", resp)

# 2. Giris yap
resp = requests.post(f"{BASE}/auth/login", data={
    "username": "buraq@gmail.com",
    "password": "test123456"
})
print_response("2. GIRIS (LOGIN)", resp)
token = resp.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {token}"}
print(f"\nToken alindi: {token[:40]}...")

# 3. /me endpoint
resp = requests.get(f"{BASE}/auth/me", headers=HEADERS)
print_response("3. MEVCUT KULLANICI (/me)", resp)

# 4. THYAO alisi - 1
resp = requests.post(f"{BASE}/transactions/", json={
    "stock_symbol": "THYAO",
    "stock_name": "Turk Hava Yollari",
    "transaction_type": "BUY",
    "quantity": 100,
    "price_per_unit": 245.50,
    "commission": 12.50,
    "notes": "Uzun vadeli yatirim"
}, headers=HEADERS)
print_response("4. ISLEM EKLE (THYAO 100 adet @ 245.50 TL)", resp)

# 5. THYAO alisi - 2
resp = requests.post(f"{BASE}/transactions/", json={
    "stock_symbol": "THYAO",
    "stock_name": "Turk Hava Yollari",
    "transaction_type": "BUY",
    "quantity": 50,
    "price_per_unit": 260.00,
    "commission": 6.25,
    "notes": "Ek alim"
}, headers=HEADERS)
print_response("5. ISLEM EKLE (THYAO 50 adet @ 260.00 TL)", resp)

# 6. ASELS alisi
resp = requests.post(f"{BASE}/transactions/", json={
    "stock_symbol": "ASELS",
    "stock_name": "Aselsan",
    "transaction_type": "BUY",
    "quantity": 200,
    "price_per_unit": 52.30,
    "commission": 5.00,
}, headers=HEADERS)
print_response("6. ISLEM EKLE (ASELS 200 adet @ 52.30 TL)", resp)

# 7. Islem listesi
resp = requests.get(f"{BASE}/transactions/", headers=HEADERS)
print_response("7. ISLEM LISTESI", resp)

# 8. Portfoy ozeti
resp = requests.get(f"{BASE}/transactions/portfolio/summary", headers=HEADERS)
print_response("8. PORTFOLYO OZETI", resp)

# 9. Tekil hisse ozeti (THYAO)
resp = requests.get(f"{BASE}/transactions/portfolio/THYAO", headers=HEADERS)
print_response("9. THYAO HISSE OZETI", resp)

print("\n" + "="*50)
print("  TESTLER TAMAMLANDI!")
print("="*50)
