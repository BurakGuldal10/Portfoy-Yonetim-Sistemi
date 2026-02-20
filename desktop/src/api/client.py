"""
API Client - Backend API'ye bağlantı
======================================
FastAPI backend'e HTTP istekleri gönderir.
"""

import requests
import json
from typing import Optional, Dict, Any
from requests.exceptions import RequestException, Timeout, ConnectionError


class APIClient:
    """Backend API ile iletişim kuran sınıf."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Args:
            base_url: API server adresi (default: localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self.timeout = 10  # saniye

    def set_token(self, token: str):
        """JWT token'ı ayarla."""
        self.token = token
        self.headers["Authorization"] = f"Bearer {token}"

    def clear_token(self):
        """Token'ı temizle."""
        self.token = None
        self.headers.pop("Authorization", None)

    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        HTTP isteği gönder.

        Args:
            method: HTTP metodu (GET, POST, PUT, DELETE)
            endpoint: API endpoint'i (/api/auth/register vb)
            data: POST/PUT body'si
            params: Query parameters

        Returns:
            Response JSON

        Raises:
            APIError: API hatası durumunda
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method == "GET":
                response = requests.get(
                    url,
                    headers=self.headers,
                    params=params,
                    timeout=self.timeout
                )
            elif method == "POST":
                response = requests.post(
                    url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=self.timeout
                )
            elif method == "PUT":
                response = requests.put(
                    url,
                    headers=self.headers,
                    json=data,
                    timeout=self.timeout
                )
            elif method == "DELETE":
                response = requests.delete(
                    url,
                    headers=self.headers,
                    timeout=self.timeout
                )
            else:
                raise ValueError(f"Bilinmeyen HTTP metodu: {method}")

            # Status code kontrolü
            if response.status_code >= 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("detail", "Bilinmeyen hata")
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                raise APIError(f"{response.status_code}: {error_msg}")

            # Response döndür
            if response.status_code == 204:  # No Content
                return {}

            return response.json()

        except (ConnectionError, Timeout):
            raise APIError("🔴 Sunucuya bağlanılamıyor. Lütfen API sunucusunun çalıştığını kontrol edin.")
        except RequestException as e:
            raise APIError(f"İstek hatası: {str(e)}")
        except json.JSONDecodeError:
            raise APIError("Sunucu yanıtı geçersiz JSON format'ında")

    # ========================================================================
    # AUTH ENDPOINTS
    # ========================================================================

    def register(self, email: str, username: str, password: str, full_name: str) -> Dict:
        """Yeni kullanıcı kaydı."""
        return self._request("POST", "/api/auth/register", data={
            "email": email,
            "username": username,
            "password": password,
            "full_name": full_name,
        })

    def login(self, email: str, password: str) -> Dict:
        """Kullanıcı girişi."""
        # OAuth2 PasswordRequestForm için form data kullanılmalı
        response = requests.post(
            f"{self.base_url}/api/auth/login",
            data={"username": email, "password": password},
            timeout=self.timeout
        )

        if response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get("detail", "Giriş başarısız")
            except:
                error_msg = "Giriş başarısız"
            raise APIError(error_msg)

        response_data = response.json()
        
        # Yanıtın doğru formatta olduğundan emin ol
        if 'access_token' not in response_data or 'user' not in response_data:
            raise APIError("API yanıtında eksik alanlar var (access_token veya user)")
        
        return response_data

    def get_current_user(self) -> Dict:
        """Mevcut kullanıcı bilgisini al."""
        return self._request("GET", "/api/auth/me")

    # ========================================================================
    # TRANSACTION ENDPOINTS
    # ========================================================================

    def create_transaction(self, data: Dict) -> Dict:
        """Yeni işlem oluştur."""
        return self._request("POST", "/api/transactions/", data=data)

    def get_transactions(self, page: int = 1, page_size: int = 20, stock_symbol: Optional[str] = None) -> Dict:
        """İşlem listesini al (sayfalanmış)."""
        params = {
            "page": page,
            "page_size": page_size,
        }
        if stock_symbol:
            params["stock_symbol"] = stock_symbol

        return self._request("GET", "/api/transactions/", params=params)

    def get_transaction(self, transaction_id: int) -> Dict:
        """Tek işlem detayını al."""
        return self._request("GET", f"/api/transactions/{transaction_id}")

    def update_transaction(self, transaction_id: int, data: Dict) -> Dict:
        """İşlemi güncelle."""
        return self._request("PUT", f"/api/transactions/{transaction_id}", data=data)

    def delete_transaction(self, transaction_id: int) -> Dict:
        """İşlemi sil."""
        return self._request("DELETE", f"/api/transactions/{transaction_id}")

    # ========================================================================
    # PORTFOLIO ENDPOINTS
    # ========================================================================

    def get_portfolio_summary(self) -> Dict:
        """Portföy özeti al."""
        return self._request("GET", "/api/transactions/portfolio/summary")

    def get_stock_summary(self, stock_symbol: str) -> Dict:
        """Hisse özeti al."""
        return self._request("GET", f"/api/transactions/portfolio/{stock_symbol}")

    # ========================================================================
    # HEALTH ENDPOINTS
    # ========================================================================

    def health_check(self) -> Dict:
        """API sağlık kontrolü."""
        try:
            return self._request("GET", "/health")
        except APIError:
            raise APIError("API sunucusu erişilemez")


class APIError(Exception):
    """API hataları için özel exception sınıfı."""
    pass
