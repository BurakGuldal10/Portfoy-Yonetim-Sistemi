"""
Pydantic Şemaları - User (Kullanıcı)
======================================
API'ye gelen ve API'den dönen verilerin doğrulanması (validation)
ve serileştirilmesi (serialization) için kullanılır.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


# ===========================================================================
# İSTEK (Request) ŞEMALlari
# ===========================================================================

class UserCreate(BaseModel):
    """Kullanıcı kayıt için gerekli alanlar."""
    email: EmailStr = Field(..., example="burak@example.com")
    username: str = Field(
        ..., min_length=3, max_length=100, example="burak123"
    )
    password: str = Field(
        ..., min_length=6, max_length=100, example="guclu_sifre_123"
    )
    full_name: Optional[str] = Field(
        None, max_length=200, example="Burak Yılmaz"
    )


class UserLogin(BaseModel):
    """Kullanıcı giriş için gerekli alanlar."""
    email: EmailStr = Field(..., example="burak@example.com")
    password: str = Field(..., example="guclu_sifre_123")


# ===========================================================================
# YANIT (Response) ŞEMALlari
# ===========================================================================

class UserResponse(BaseModel):
    """API'den dönen kullanıcı bilgileri (şifre HARİÇ)."""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy modelinden otomatik dönüşüm


class TokenResponse(BaseModel):
    """Başarılı giriş sonrası dönen JWT token bilgisi."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
