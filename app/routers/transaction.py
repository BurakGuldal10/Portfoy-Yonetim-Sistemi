"""
Transaction Router - İşlem Endpointleri
=========================================
Borsa alım/satım işlemlerinin CRUD endpointlerini ve
portföy özeti hesaplama endpointlerini tanımlar.

Tüm endpointler korumalıdır (JWT token gerektirir).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.security import get_current_user
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionListResponse,
    PortfolioSummary,
    StockSummary,
)
from app.services.portfolio_service import (
    create_transaction,
    get_user_transactions,
    get_transaction_by_id,
    update_transaction,
    delete_transaction,
    calculate_portfolio_summary,
    calculate_stock_summary,
)

# Router tanımı
router = APIRouter(
    prefix="/api/transactions",
    tags=["İşlemler (Transactions)"],
)


# ===========================================================================
# POST /api/transactions/ - Yeni İşlem Ekle
# ===========================================================================
@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni işlem ekle",
    description="Hisse alım veya satım işlemi ekler.",
)
def add_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Yeni bir borsa işlemi oluşturur.

    - **stock_symbol**: Hisse kodu (ör: THYAO, ASELS)
    - **transaction_type**: BUY (Alış) veya SELL (Satış)
    - **quantity**: Adet
    - **price_per_unit**: Birim fiyat (TL)
    - **commission**: Komisyon (opsiyonel, varsayılan 0)
    """
    transaction = create_transaction(db, current_user.id, transaction_data)
    return transaction


# ===========================================================================
# GET /api/transactions/portfolio/summary - Portföy Özeti (PORTFOLIO İLK GELMELİ!)
# ===========================================================================
@router.get(
    "/portfolio/summary",
    response_model=PortfolioSummary,
    summary="Portföy özeti",
    description="Kullanıcının tüm portföyünün özetini hesaplar.",
)
def portfolio_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının portföy özetini döndürür:
    - Toplam yatırım tutarı
    - Toplam komisyon
    - Hisse bazlı detaylı özet (ortalama maliyet, adet vb.)
    """
    return calculate_portfolio_summary(db, current_user.id)


# ===========================================================================
# GET /api/transactions/portfolio/{symbol} - Tekil Hisse Özeti
# ===========================================================================
@router.get(
    "/portfolio/{stock_symbol}",
    response_model=StockSummary,
    summary="Hisse özeti",
    description="Tek bir hisse senedinin portföy özetini hesaplar.",
)
def stock_summary(
    stock_symbol: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirtilen hisse senedinin portföy özetini döndürür:
    - Ortalama maliyet
    - Toplam alış/satış adedi
    - Net elde tutulan adet
    """
    summary = calculate_stock_summary(db, current_user.id, stock_symbol)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"'{stock_symbol.upper()}' kodlu hisseye ait işlem bulunamadı.",
        )

    return summary


# ===========================================================================
# GET /api/transactions/ - İşlem Listesi
# ===========================================================================
@router.get(
    "/",
    response_model=TransactionListResponse,
    summary="İşlem listesi",
    description="Kullanıcının tüm işlemlerini sayfalanmış olarak getirir.",
)
def list_transactions(
    page: int = Query(1, ge=1, description="Sayfa numarası"),
    page_size: int = Query(20, ge=1, le=100, description="Sayfa başına kayıt"),
    stock_symbol: Optional[str] = Query(
        None, description="Hisse koduna göre filtrele (ör: THYAO)"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Kullanıcının işlemlerini listeler.

    Sayfalama ve hisse filtresi destekler.
    En yeni işlemler önce gösterilir.
    """
    transactions, total_count = get_user_transactions(
        db, current_user.id, page, page_size, stock_symbol
    )

    return TransactionListResponse(
        transactions=transactions,
        total_count=total_count,
        page=page,
        page_size=page_size,
    )


# ===========================================================================
# GET /api/transactions/{id} - Tek İşlem Detayı
# ===========================================================================
@router.get(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="İşlem detayı",
    description="ID'ye göre tek bir işlemin detaylarını getirir.",
)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Belirtilen ID'ye sahip işlemin detaylarını döndürür."""
    transaction = get_transaction_by_id(db, transaction_id, current_user.id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="İşlem bulunamadı.",
        )

    return transaction


# ===========================================================================
# DELETE /api/transactions/{id} - İşlem Sil
# ===========================================================================
@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="İşlem sil",
    description="Belirtilen işlemi siler.",
)
def remove_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Belirtilen ID'ye sahip işlemi siler."""
    success = delete_transaction(db, transaction_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="İşlem bulunamadı veya size ait değil.",
        )


# ===========================================================================
# PUT /api/transactions/{id} - İşlem Güncelle
# ===========================================================================
@router.put(
    "/{transaction_id}",
    response_model=TransactionResponse,
    summary="İşlem güncelle",
    description="Mevcut bir işlemi günceller.",
)
def update_existing_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirtilen ID'ye sahip işlemi günceller.

    Güncelleme alanları opsiyoneldir - sadece gönderdikleriniz güncellenecektir.
    """
    # Update data dict'e çevir (None değerleri hariç)
    update_dict = transaction_data.model_dump(exclude_none=True)

    updated = update_transaction(db, transaction_id, current_user.id, update_dict)

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="İşlem bulunamadı veya size ait değil.",
        )

    return updated
