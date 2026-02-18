"""
Transaction Testleri
====================
İşlem CRUD ve portföy hesaplama testleri.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def authenticated_client(client: TestClient, test_user_data):
    """Giriş yapılmış test client'ı."""
    # Kullanıcı oluştur ve giriş yap
    client.post("/api/auth/register", json=test_user_data)
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token}"}
    return client


def test_create_transaction(authenticated_client: TestClient, test_transaction_data):
    """Yeni işlem oluştur."""
    response = authenticated_client.post(
        "/api/transactions/",
        json=test_transaction_data
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["stock_symbol"] == "THYAO"
    assert data["quantity"] == 100
    assert data["price_per_unit"] == 245.50
    assert data["total_amount"] == 100 * 245.50  # quantity * price_per_unit
    assert data["commission"] == 12.50


def test_get_transactions_list(authenticated_client: TestClient, test_transaction_data):
    """İşlem listesini al."""
    # Birkaç işlem ekle
    for i in range(3):
        authenticated_client.post("/api/transactions/", json=test_transaction_data)
    
    response = authenticated_client.get("/api/transactions/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 3
    assert len(data["transactions"]) == 3
    assert data["page"] == 1
    assert data["page_size"] == 20


def test_get_transaction_by_id(authenticated_client: TestClient, test_transaction_data):
    """ID'ye göre işlem al."""
    # İşlem oluştur
    create_response = authenticated_client.post(
        "/api/transactions/",
        json=test_transaction_data
    )
    transaction_id = create_response.json()["id"]
    
    # İşlemi al
    response = authenticated_client.get(f"/api/transactions/{transaction_id}")
    
    assert response.status_code == 200
    assert response.json()["id"] == transaction_id
    assert response.json()["stock_symbol"] == "THYAO"


def test_get_nonexistent_transaction(authenticated_client: TestClient):
    """Var olmayan işlem."""
    response = authenticated_client.get("/api/transactions/9999")
    assert response.status_code == 404


def test_update_transaction(authenticated_client: TestClient, test_transaction_data):
    """İşlem güncelle."""
    # İşlem oluştur
    create_response = authenticated_client.post(
        "/api/transactions/",
        json=test_transaction_data
    )
    transaction_id = create_response.json()["id"]
    
    # Güncelle
    update_data = {
        "quantity": 150,
        "price_per_unit": 250.00,
        "notes": "Güncellenen not"
    }
    
    response = authenticated_client.put(
        f"/api/transactions/{transaction_id}",
        json=update_data
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 150
    assert data["price_per_unit"] == 250.00
    assert data["total_amount"] == 150 * 250.00  # Otomatik hesaplanan
    assert data["notes"] == "Güncellenen not"


def test_delete_transaction(authenticated_client: TestClient, test_transaction_data):
    """İşlem sil."""
    # İşlem oluştur
    create_response = authenticated_client.post(
        "/api/transactions/",
        json=test_transaction_data
    )
    transaction_id = create_response.json()["id"]
    
    # Sil
    response = authenticated_client.delete(f"/api/transactions/{transaction_id}")
    assert response.status_code == 204
    
    # Tekrar al (artık olmamalı)
    response = authenticated_client.get(f"/api/transactions/{transaction_id}")
    assert response.status_code == 404


def test_portfolio_summary(authenticated_client: TestClient, test_transaction_data):
    """Portföy özeti."""
    # İşlemler ekle
    authenticated_client.post("/api/transactions/", json=test_transaction_data)
    
    # Satış işlemi
    sell_data = test_transaction_data.copy()
    sell_data["transaction_type"] = "SELL"
    sell_data["quantity"] = 50
    authenticated_client.post("/api/transactions/", json=sell_data)
    
    # Portföy özetini al
    response = authenticated_client.get("/api/transactions/portfolio/summary")
    
    assert response.status_code == 200
    data = response.json()
    assert data["stock_count"] == 1
    assert len(data["stocks"]) == 1
    
    # Hisse özeti kontrolü
    stock = data["stocks"][0]
    assert stock["stock_symbol"] == "THYAO"
    assert stock["total_buy_quantity"] == 100
    assert stock["total_sell_quantity"] == 50
    assert stock["total_quantity"] == 50  # 100 - 50


def test_stock_summary(authenticated_client: TestClient, test_transaction_data):
    """Hisse özeti."""
    # İşlem ekle
    authenticated_client.post("/api/transactions/", json=test_transaction_data)
    
    # Hisse özetini al
    response = authenticated_client.get("/api/transactions/portfolio/THYAO")
    
    assert response.status_code == 200
    data = response.json()
    assert data["stock_symbol"] == "THYAO"
    assert data["total_quantity"] == 100
    assert data["average_cost"] == 245.50


def test_stock_summary_nonexistent(authenticated_client: TestClient):
    """Var olmayan hisse."""
    response = authenticated_client.get("/api/transactions/portfolio/NONEXIST")
    assert response.status_code == 404


def test_filter_transactions_by_symbol(authenticated_client: TestClient, test_transaction_data):
    """Hisse koduna göre filtrele."""
    # THYAO işlemi ekle
    authenticated_client.post("/api/transactions/", json=test_transaction_data)
    
    # ASELS işlemi ekle
    asels_data = test_transaction_data.copy()
    asels_data["stock_symbol"] = "ASELS"
    authenticated_client.post("/api/transactions/", json=asels_data)
    
    # THYAO'ya göre filtrele
    response = authenticated_client.get("/api/transactions/?stock_symbol=THYAO")
    
    assert response.status_code == 200
    data = response.json()
    assert data["total_count"] == 1
    assert data["transactions"][0]["stock_symbol"] == "THYAO"


def test_transaction_requires_auth(client: TestClient, test_transaction_data):
    """İşlem endpointleri kimlik doğrulama gerektirir."""
    response = client.post("/api/transactions/", json=test_transaction_data)
    assert response.status_code == 403  # Forbidden (token yok)
