"""
User (Kullanıcı) Modeli
========================
Kullanıcı bilgilerini ve kimlik doğrulaması için gerekli alanları tanımlar.
"""

from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    Kullanıcı tablosu.

    Alanlar:
        id          : Benzersiz kullanıcı kimliği (otomatik artan)
        email       : Kullanıcının e-posta adresi (benzersiz, giriş için kullanılır)
        username    : Kullanıcı adı (benzersiz)
        hashed_password : Hashlenmiş şifre (düz metin olarak ASLA saklanmaz)
        full_name   : Kullanıcının tam adı
        is_active   : Hesap aktif mi? (pasif hesaplar giriş yapamaz)
        created_at  : Hesap oluşturulma tarihi
        updated_at  : Son güncelleme tarihi
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # ---------------------------------------------------------------------------
    # İlişki (Relationship)
    # ---------------------------------------------------------------------------
    # Bir kullanıcının birden fazla işlemi olabilir (One-to-Many)
    # back_populates: Transaction modelindeki "owner" alanına bağlanır
    # cascade="all, delete-orphan": Kullanıcı silinirse işlemleri de silinir
    transactions = relationship(
        "Transaction",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",  # İlişkili verileri otomatik yükle
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
