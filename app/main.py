"""
Finans Takip - Portföy Yönetim Sistemi
========================================
Ana uygulama dosyası. FastAPI uygulamasını oluşturur,
router'ları bağlar ve veritabanı tablolarını başlatır.

Çalıştırma:
    uvicorn app.main:app --reload --port 8000

Swagger UI:
    http://localhost:8000/docs

ReDoc:
    http://localhost:8000/redoc
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import engine, Base
from app.logger import get_logger

# Modelleri import et (tabloların oluşturulması için gerekli)
from app.models.user import User          # noqa: F401
from app.models.transaction import Transaction  # noqa: F401

# Router'ları import et
from app.routers import auth, transaction

# Logger
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Veritabanı Tablolarını Oluştur
# ---------------------------------------------------------------------------
# Not: Production'da Alembic migration kullanılmalıdır.
# Bu yöntem sadece geliştirme ortamı için uygundur.
try:
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Veritabanı tabloları başarıyla oluşturuldu/kontrol edildi.")
except Exception as e:
    logger.error(f"❌ Veritabanı tablolarını oluştururken hata: {e}")


# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # ReDoc
)

logger.info(f"🚀 Uygulamada başlatıldı: {settings.APP_NAME} v{settings.APP_VERSION}")
logger.info(f"📦 Ortam: {settings.ENVIRONMENT}")


# ---------------------------------------------------------------------------
# CORS Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                           # Geliştirme için tüm originlere izin ver
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
logger.debug("📋 CORS ayarları: origins=ALL (*)")


# ---------------------------------------------------------------------------
# Router'ları Bağla
# ---------------------------------------------------------------------------
app.include_router(auth.router)
app.include_router(transaction.router)
logger.info("✅ Router'lar başarıyla bağlandı.")


# ---------------------------------------------------------------------------
# Kök Endpoint (Health Check)
# ---------------------------------------------------------------------------
@app.get(
    "/",
    tags=["Genel"],
    summary="API Sağlık Kontrolü",
)
def root():
    """
    API'nin çalışıp çalışmadığını kontrol eder.
    Basit bir sağlık kontrolü endpointidir.
    """
    return {
        "message": "🚀 Finans Takip API çalışıyor!",
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get(
    "/health",
    tags=["Genel"],
    summary="Detaylı Sağlık Kontrolü",
)
def health_check():
    """Detaylı sağlık kontrolü - veritabanı bağlantısı dahil."""
    from sqlalchemy import text
    from app.database import SessionLocal

    db_status = "healthy"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "running",
        "database": db_status,
        "version": settings.APP_VERSION,
    }


# ---------------------------------------------------------------------------
# Global Exception Handler'lar
# ---------------------------------------------------------------------------

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """Validation hatalarını log et ve döndür."""
    logger.warning(f"⚠️  Validation hatası: {request.url.path}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Giriş verisi doğrulaması başarısız oldu.",
            "errors": [
                {
                    "field": list(error["loc"])[1] if len(error["loc"]) > 1 else error["loc"][0],
                    "message": error["msg"],
                    "type": error["type"]
                }
                for error in exc.errors()
            ]
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Beklenmedik hatalardan günlüğe al ve döndür."""
    logger.error(f"❌ Beklenmedik hata {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Sunucu hatası oluştu. Lütfen daha sonra deneyin."},
    )
