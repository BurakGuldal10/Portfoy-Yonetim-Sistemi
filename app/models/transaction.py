"""
Transaction (İşlem) Modeli
============================
Kullanıcıların borsa alım/satım işlemlerini tutan tablo.
Her işlem bir kullanıcıya aittir (Foreign Key ile bağlı).
"""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship

from app.database import Base


class TransactionType(str, PyEnum):
    """
    İşlem tipi.
    BUY  = Alış işlemi
    SELL = Satış işlemi
    """
    BUY = "BUY"
    SELL = "SELL"


class Transaction(Base):
    """
    İşlem tablosu.

    Alanlar:
        id              : Benzersiz işlem kimliği
        user_id         : İşlemi yapan kullanıcının ID'si (Foreign Key)
        stock_symbol    : Hisse senedi kodu (ör: THYAO, ASELS, SISE)
        stock_name      : Hisse senedi tam adı (ör: Türk Hava Yolları)
        transaction_type: İşlem tipi (BUY / SELL)
        quantity        : Adet (kaç lot/hisse alındı/satıldı)
        price_per_unit  : Birim fiyatı (alış veya satış fiyatı, TL)
        total_amount    : Toplam tutar (quantity * price_per_unit)
        commission      : Komisyon ücreti (TL, varsayılan 0)
        transaction_date: İşlem tarihi
        notes           : İsteğe bağlı not alanı
        created_at      : Kayıt oluşturulma tarihi
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Kullanıcı ilişkisi (Foreign Key)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Hisse bilgileri
    stock_symbol = Column(String(20), nullable=False, index=True)  # Ör: THYAO
    stock_name = Column(String(200), nullable=True)                # Ör: Türk Hava Yolları

    # İşlem detayları
    transaction_type = Column(
        Enum(TransactionType, native_enum=False),
        nullable=False,
        default=TransactionType.BUY,
    )
    quantity = Column(Float, nullable=False)           # Adet
    price_per_unit = Column(Float, nullable=False)     # Birim fiyat (TL)
    total_amount = Column(Float, nullable=False)       # Toplam tutar (TL)
    commission = Column(Float, nullable=False, default=0.0)  # Komisyon (TL)

    # Tarih bilgileri
    transaction_date = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Ek bilgi
    notes = Column(String(500), nullable=True)

    # ---------------------------------------------------------------------------
    # İlişki (Relationship)
    # ---------------------------------------------------------------------------
    # Bu işlem hangi kullanıcıya ait?
    owner = relationship("User", back_populates="transactions")

    def __repr__(self):
        return (
            f"<Transaction(id={self.id}, symbol='{self.stock_symbol}', "
            f"type={self.transaction_type}, qty={self.quantity}, "
            f"price={self.price_per_unit})>"
        )
