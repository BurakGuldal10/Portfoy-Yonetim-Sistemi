"""
Uygulama Konfigürasyon Ayarları
================================
.env dosyasından ortam değişkenlerini okur ve uygulama genelinde
kullanılacak ayarları merkezi bir yerden yönetir.
"""

import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


class Settings:
    """Uygulama ayarlarını tutan sınıf."""

    # Veritabanı bağlantı URL'si
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/finans_takip"
    )

    # JWT Token Ayarları
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # CORS Ayarları
    ALLOWED_ORIGINS: list = [
        item.strip() for item in os.getenv(
            "ALLOWED_ORIGINS", 
            "http://localhost:3000,http://localhost:8000"
        ).split(",")
    ]

    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    def __init__(self):
        """Settings validasyonu"""
        # Production'da SECRET_KEY zorunlu
        if self.ENVIRONMENT == "production" and not self.SECRET_KEY:
            raise ValueError(
                "Production ortamında SECRET_KEY çevresel değişkeni ayarlanması zorunludur!"
            )
        
        # Development'da fallback key, ama warning ver
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "development":
                self.SECRET_KEY = "dev-insecure-key-change-in-production"
                print(" WARNING: Using insecure SECRET_KEY in development!")

    # Uygulama Bilgileri
    APP_NAME: str = "Finans Takip - Portföy Yönetim Sistemi"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Borsa işlemlerinizi takip edin, kar/zarar analizi yapın."

# Tek bir settings nesnesi oluştur (Singleton pattern)
settings = Settings()

