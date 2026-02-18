"""
Auth Testleri
==============
Kullanıcı kayıt ve giriş işlemlerinin testleri.
"""

import pytest
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient, test_user_data):
    """Başarılı kullanıcı kaydı."""
    response = client.post(
        "/api/auth/register",
        json=test_user_data
    )
    
    assert response.status_code == 201
    assert response.json()["email"] == test_user_data["email"]
    assert response.json()["username"] == test_user_data["username"]
    assert "hashed_password" not in response.json()  # Şifre dönmemeli


def test_register_duplicate_email(client: TestClient, test_user_data):
    """Aynı e-posta ile kayıt başarısız."""
    # İlk kaydı başarılı yap
    client.post("/api/auth/register", json=test_user_data)
    
    # Aynı email ile ikinci kayıt
    duplicate_user = test_user_data.copy()
    duplicate_user["username"] = "different_user"
    
    response = client.post(
        "/api/auth/register",
        json=duplicate_user
    )
    
    assert response.status_code == 400
    assert "başarısız" in response.json()["detail"].lower()


def test_register_duplicate_username(client: TestClient, test_user_data):
    """Aynı username ile kayıt başarısız."""
    # İlk kaydı başarılı yap
    client.post("/api/auth/register", json=test_user_data)
    
    # Aynı username ile ikinci kayıt
    duplicate_user = test_user_data.copy()
    duplicate_user["email"] = "different@example.com"
    
    response = client.post(
        "/api/auth/register",
        json=duplicate_user
    )
    
    assert response.status_code == 400


def test_register_invalid_email(client: TestClient, test_user_data):
    """Geçersiz e-posta formatı."""
    invalid_user = test_user_data.copy()
    invalid_user["email"] = "invalid-email"
    
    response = client.post(
        "/api/auth/register",
        json=invalid_user
    )
    
    assert response.status_code == 422  # Validation error


def test_login_success(client: TestClient, test_user_data):
    """Başarılı giriş."""
    # Önce kullanıcı oluştur
    client.post("/api/auth/register", json=test_user_data)
    
    # Giriş yap
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["email"],  # OAuth2 username alanını email olarak kullan
            "password": test_user_data["password"]
        }
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient, test_user_data):
    """Yanlış şifre."""
    # Kullanıcı oluştur
    client.post("/api/auth/register", json=test_user_data)
    
    # Yanlış şifre ile giriş
    response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["email"],
            "password": "wrong_password"
        }
    )
    
    assert response.status_code == 401
    assert "hatalı" in response.json()["detail"].lower()


def test_login_nonexistent_user(client: TestClient):
    """Var olmayan kullanıcı."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": "nonexistent@example.com",
            "password": "any_password"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user(client: TestClient, test_user_data):
    """Mevcut kullanıcı bilgisini al."""
    # Kullanıcı kaydı ve giriş
    client.post("/api/auth/register", json=test_user_data)
    
    login_response = client.post(
        "/api/auth/login",
        data={
            "username": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    
    # Kullanıcı bilgisini al
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json()["email"] == test_user_data["email"]
    assert response.json()["username"] == test_user_data["username"]


def test_get_current_user_no_token(client: TestClient):
    """Token olmadan /me erişimi başarısız."""
    response = client.get("/api/auth/me")
    assert response.status_code == 403  # Forbidden


def test_get_current_user_invalid_token(client: TestClient):
    """Geçersiz token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
