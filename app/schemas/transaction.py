"""
Pydantic Şemaları - Transaction (İşlem)
=========================================
Borsa alım/satım işlemleri için veri doğrulama ve serileştirme şemaları.
"""

from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from app.models.transaction import TransactionType


# ===========================================================================
# İSTEK (Request) ŞEMALlari
# ===========================================================================

class TransactionCreate(BaseModel):
    """Yeni işlem oluşturmak için gerekli alanlar."""
    stock_symbol: str = Field(
        ..., min_length=1, max_length=20, example="THYAO",
        description="Hisse senedi borsa kodu",
    )
    stock_name: Optional[str] = Field(
        None, max_length=200, example="Türk Hava Yolları",
        description="Hisse senedi tam adı",
    )
    transaction_type: TransactionType = Field(
        ..., example="BUY",
        description="İşlem tipi: BUY (Alış) veya SELL (Satış)",
    )
    quantity: float = Field(
        ..., gt=0, example=100,
        description="Alınan/Satılan hisse adedi",
    )
    price_per_unit: float = Field(
        ..., gt=0, example=245.50,
        description="Birim hisse fiyatı (TL)",
    )
    commission: float = Field(
        default=0.0, ge=0, example=12.50,
        description="Komisyon ücreti (TL)",
    )
    transaction_date: Optional[datetime] = Field(
        None,
        description="İşlem tarihi (boş bırakılırsa şu anki zaman kullanılır)",
    )
    notes: Optional[str] = Field(
        None, max_length=500, example="Uzun vadeli yatırım",
        description="İşleme ait not",
    )


class TransactionUpdate(BaseModel):
    """Mevcut işlemi güncellemek için kullanılan alanlar (tümü opsiyonel)."""
    stock_symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    stock_name: Optional[str] = Field(None, max_length=200)
    transaction_type: Optional[TransactionType] = None
    quantity: Optional[float] = Field(None, gt=0)
    price_per_unit: Optional[float] = Field(None, gt=0)
    commission: Optional[float] = Field(None, ge=0)
    transaction_date: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=500)


# ===========================================================================
# YANIT (Response) ŞEMALlari
# ===========================================================================

class TransactionResponse(BaseModel):
    """API'den dönen işlem bilgileri."""
    id: int
    stock_symbol: str
    stock_name: Optional[str] = None
    transaction_type: TransactionType
    quantity: float
    price_per_unit: float
    total_amount: float
    commission: float
    transaction_date: datetime
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """İşlem listesi yanıtı (sayfalama bilgisiyle birlikte)."""
    transactions: List[TransactionResponse]
    total_count: int
    page: int
    page_size: int


# ===========================================================================
# PORTFÖY ÖZETİ ŞEMALlari
# ===========================================================================

class StockSummary(BaseModel):
    """Tek bir hisse senedinin portföy özeti."""
    stock_symbol: str
    stock_name: Optional[str] = None
    total_quantity: float          # Toplam elde tutulan adet
    average_cost: float            # Ortalama maliyet (TL)
    total_invested: float          # Toplam yatırım tutarı (TL)
    total_commission: float        # Toplam komisyon (TL)
    total_buy_quantity: float      # Toplam alış adedi
    total_sell_quantity: float     # Toplam satış adedi


class PortfolioSummary(BaseModel):
    """Kullanıcının tüm portföy özeti."""
    user_id: int
    total_invested: float          # Portföy toplam yatırım
    total_commission: float        # Toplam ödenen komisyon
    stock_count: int               # Portföydeki farklı hisse sayısı
    stocks: List[StockSummary]     # Her hissenin detaylı özeti
