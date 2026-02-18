"""
Portfolio Service - Portföy Hesaplama İş Mantığı
==================================================
Kullanıcının portföy durumunu hesaplar:
- Ortalama maliyet hesaplama
- Kar/zarar analizi
- Hisse bazlı ve genel portföy özeti
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import (
    StockSummary,
    PortfolioSummary,
    TransactionCreate,
)
from app.logger import get_logger

logger = get_logger(__name__)


# ===========================================================================
# İŞLEM CRUD İŞLEMLERİ
# ===========================================================================

def create_transaction(
    db: Session, user_id: int, transaction_data: TransactionCreate
) -> Transaction:
    """
    Yeni bir alım/satım işlemi oluşturur.

    total_amount otomatik olarak hesaplanır: quantity * price_per_unit

    Args:
        db: Veritabanı oturumu
        user_id: İşlemi yapan kullanıcının ID'si
        transaction_data: İşlem verileri

    Returns:
        Oluşturulan Transaction nesnesi
    """
    # Toplam tutarı hesapla
    total_amount = transaction_data.quantity * transaction_data.price_per_unit

    new_transaction = Transaction(
        user_id=user_id,
        stock_symbol=transaction_data.stock_symbol.upper(),  # Hep büyük harf
        stock_name=transaction_data.stock_name,
        transaction_type=transaction_data.transaction_type,
        quantity=transaction_data.quantity,
        price_per_unit=transaction_data.price_per_unit,
        total_amount=total_amount,
        commission=transaction_data.commission,
        transaction_date=transaction_data.transaction_date,
        notes=transaction_data.notes,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


def get_user_transactions(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    stock_symbol: Optional[str] = None,
) -> tuple[List[Transaction], int]:
    """
    Kullanıcının işlemlerini sayfalanmış olarak getirir.

    Args:
        db: Veritabanı oturumu
        user_id: Kullanıcı ID'si
        page: Sayfa numarası (1'den başlar)
        page_size: Sayfa başına işlem sayısı
        stock_symbol: Opsiyonel hisse filtresi

    Returns:
        (İşlem listesi, toplam işlem sayısı) tuple'ı
    """
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    # Hisse filtresi varsa uygula
    if stock_symbol:
        query = query.filter(
            Transaction.stock_symbol == stock_symbol.upper()
        )

    # Toplam sayıyı al
    total_count = query.count()

    # Sayfalama ve sıralama (en yeni işlem önce)
    transactions = (
        query
        .order_by(Transaction.transaction_date.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return transactions, total_count


def get_transaction_by_id(
    db: Session, transaction_id: int, user_id: int
) -> Optional[Transaction]:
    """
    ID'ye göre tek bir işlemi getirir (sadece kendi işlemini görebilir).

    Args:
        db: Veritabanı oturumu
        transaction_id: İşlem ID'si
        user_id: Kullanıcı ID'si (yetki kontrolü)

    Returns:
        Transaction nesnesi veya None
    """
    return (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id,
        )
        .first()
    )


def update_transaction(
    db: Session, transaction_id: int, user_id: int, transaction_data: dict
) -> Optional[Transaction]:
    """
    Mevcut bir işlemi günceller.

    Güncellenen alanlardan biri price_per_unit veya quantity ise,
    total_amount otomatik olarak yeniden hesaplanır.

    Args:
        db: Veritabanı oturumu
        transaction_id: Güncellenecek işlem ID'si
        user_id: Kullanıcı ID'si (yetki kontrolü)
        transaction_data: Güncellenecek alanlar (dict)

    Returns:
        Güncellenmiş Transaction nesnesi veya None (bulunamazsa)
    """
    transaction = get_transaction_by_id(db, transaction_id, user_id)

    if not transaction:
        return None

    # Güncelleme işlemi
    for field, value in transaction_data.items():
        if value is not None:
            setattr(transaction, field, value)

    # Eğer quantity veya price_per_unit güncellenirse, total_amount'ı yeniden hesapla
    if "quantity" in transaction_data or "price_per_unit" in transaction_data:
        transaction.total_amount = transaction.quantity * transaction.price_per_unit

    # stock_symbol her zaman büyük harf
    if hasattr(transaction, "stock_symbol"):
        transaction.stock_symbol = transaction.stock_symbol.upper()

    db.commit()
    db.refresh(transaction)
    return transaction


def delete_transaction(
    db: Session, transaction_id: int, user_id: int
) -> bool:
    """
    Bir işlemi siler.

    Args:
        db: Veritabanı oturumu
        transaction_id: Silinecek işlem ID'si
        user_id: Kullanıcı ID'si (yetki kontrolü)

    Returns:
        True: başarıyla silindi, False: işlem bulunamadı
    """
    transaction = get_transaction_by_id(db, transaction_id, user_id)

    if not transaction:
        return False

    db.delete(transaction)
    db.commit()
    return True


# ===========================================================================
# PORTFÖY HESAPLAMA FONKSİYONLARI
# ===========================================================================

def calculate_stock_summary(
    db: Session, user_id: int, stock_symbol: str
) -> Optional[StockSummary]:
    """
    Tek bir hisse senedi için portföy özetini hesaplar.

    Hesaplama mantığı:
        - Toplam alış adedi ve tutarı
        - Toplam satış adedi
        - Net elde tutulan adet = alış - satış
        - Ortalama maliyet = toplam alış tutarı / toplam alış adedi

    Args:
        db: Veritabanı oturumu
        user_id: Kullanıcı ID'si
        stock_symbol: Hisse kodu (ör: THYAO)

    Returns:
        StockSummary nesnesi veya None (işlem yoksa)
    """
    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.stock_symbol == stock_symbol.upper(),
        )
        .all()
    )

    if not transactions:
        return None

    # Değişkenleri başlat
    total_buy_quantity = 0.0
    total_buy_amount = 0.0
    total_sell_quantity = 0.0
    total_commission = 0.0
    stock_name = None

    for t in transactions:
        if t.transaction_type == TransactionType.BUY:
            total_buy_quantity += t.quantity
            total_buy_amount += t.total_amount
        elif t.transaction_type == TransactionType.SELL:
            total_sell_quantity += t.quantity

        total_commission += t.commission

        # En son işlemdeki hisse adını kullan
        if t.stock_name:
            stock_name = t.stock_name

    # Net elde tutulan adet
    net_quantity = total_buy_quantity - total_sell_quantity

    # Ortalama maliyet (sıfıra bölme koruması)
    average_cost = (
        total_buy_amount / total_buy_quantity
        if total_buy_quantity > 0
        else 0.0
    )

    return StockSummary(
        stock_symbol=stock_symbol.upper(),
        stock_name=stock_name,
        total_quantity=round(net_quantity, 4),
        average_cost=round(average_cost, 4),
        total_invested=round(total_buy_amount, 2),
        total_commission=round(total_commission, 2),
        total_buy_quantity=round(total_buy_quantity, 4),
        total_sell_quantity=round(total_sell_quantity, 4),
    )


def calculate_portfolio_summary(
    db: Session, user_id: int
) -> PortfolioSummary:
    """
    Kullanıcının tüm portföyünün özetini hesaplar.

    Tüm hisse senetlerini gruplar ve her biri için StockSummary hesaplar.

    Args:
        db: Veritabanı oturumu
        user_id: Kullanıcı ID'si

    Returns:
        PortfolioSummary nesnesi
    """
    # Kullanıcının portföyündeki benzersiz hisse kodlarını al
    unique_symbols = (
        db.query(Transaction.stock_symbol)
        .filter(Transaction.user_id == user_id)
        .distinct()
        .all()
    )

    stocks: List[StockSummary] = []
    total_invested = 0.0
    total_commission = 0.0

    for (symbol,) in unique_symbols:
        summary = calculate_stock_summary(db, user_id, symbol)
        if summary:
            stocks.append(summary)
            total_invested += summary.total_invested
            total_commission += summary.total_commission

    return PortfolioSummary(
        user_id=user_id,
        total_invested=round(total_invested, 2),
        total_commission=round(total_commission, 2),
        stock_count=len(stocks),
        stocks=stocks,
    )
