"""
Data Models - API'den gelen verileri temsil eden sınıflar
===========================================================
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    """Kullanıcı modeli."""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """Dict'ten User nesnesi oluştur."""
        return cls(
            id=data['id'],
            email=data['email'],
            username=data['username'],
            full_name=data.get('full_name'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        )


@dataclass
class Transaction:
    """İşlem modeli."""
    id: int
    stock_symbol: str
    stock_name: Optional[str]
    transaction_type: str  # BUY veya SELL
    quantity: float
    price_per_unit: float
    total_amount: float
    commission: float
    transaction_date: datetime
    notes: Optional[str]
    created_at: datetime

    @classmethod
    def from_dict(cls, data: dict) -> 'Transaction':
        """Dict'ten Transaction nesnesi oluştur."""
        return cls(
            id=data['id'],
            stock_symbol=data['stock_symbol'],
            stock_name=data.get('stock_name'),
            transaction_type=data['transaction_type'],
            quantity=data['quantity'],
            price_per_unit=data['price_per_unit'],
            total_amount=data['total_amount'],
            commission=data.get('commission', 0),
            transaction_date=datetime.fromisoformat(data['transaction_date'].replace('Z', '+00:00')),
            notes=data.get('notes'),
            created_at=datetime.fromisoformat(data['created_at'].replace('Z', '+00:00'))
        )


@dataclass
class StockSummary:
    """Hisse özeti modeli."""
    stock_symbol: str
    stock_name: Optional[str]
    total_quantity: float
    average_cost: float
    total_invested: float
    total_commission: float
    total_buy_quantity: float
    total_sell_quantity: float

    @classmethod
    def from_dict(cls, data: dict) -> 'StockSummary':
        """Dict'ten StockSummary nesnesi oluştur."""
        return cls(
            stock_symbol=data['stock_symbol'],
            stock_name=data.get('stock_name'),
            total_quantity=data['total_quantity'],
            average_cost=data['average_cost'],
            total_invested=data['total_invested'],
            total_commission=data['total_commission'],
            total_buy_quantity=data['total_buy_quantity'],
            total_sell_quantity=data['total_sell_quantity'],
        )


@dataclass
class PortfolioSummary:
    """Portföy özeti modeli."""
    user_id: int
    total_invested: float
    total_commission: float
    stock_count: int
    stocks: List[StockSummary]

    @classmethod
    def from_dict(cls, data: dict) -> 'PortfolioSummary':
        """Dict'ten PortfolioSummary nesnesi oluştur."""
        return cls(
            user_id=data['user_id'],
            total_invested=data['total_invested'],
            total_commission=data['total_commission'],
            stock_count=data['stock_count'],
            stocks=[StockSummary.from_dict(stock) for stock in data['stocks']],
        )
