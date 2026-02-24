"""
UI Pages - Sayfa bileşenleri
=============================
Her sayfa için ayrı modül
"""

def __getattr__(name):
    """Lazy import for page classes"""
    if name == 'DashboardPage':
        from .dashboard_page import DashboardPage
        return DashboardPage
    elif name == 'TransactionHistoryPage':
        from .transaction_history_page import TransactionHistoryPage
        return TransactionHistoryPage
    elif name == 'PlaceholderPage':
        from .placeholder_page import PlaceholderPage
        return PlaceholderPage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    'DashboardPage',
    'TransactionHistoryPage',
    'PlaceholderPage',
]
