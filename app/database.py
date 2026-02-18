"""
Veritabanı Bağlantı Modülü
===========================
SQLAlchemy engine, session ve Base modelini yapılandırır.
Tüm veritabanı işlemleri bu modül üzerinden yönetilir.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# ---------------------------------------------------------------------------
# SQLAlchemy Engine
# ---------------------------------------------------------------------------
# pool_pre_ping: Bağlantının hâlâ canlı olup olmadığını kontrol eder.
# Bu sayede "connection closed" hatalarının önüne geçilir.

# SQLite için özel ayarlar (geliştirme ortamı)
_engine_kwargs = {
    "pool_pre_ping": True,
    "echo": False,  # SQL sorgularını konsola yazdırmak için True yapılabilir
}

if settings.DATABASE_URL.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}
    _engine_kwargs.pop("pool_pre_ping")  # SQLite pool_pre_ping desteklemez

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

# ---------------------------------------------------------------------------
# Session Factory
# ---------------------------------------------------------------------------
# autocommit=False : Her şeyi açıkça commit etmemiz gerekir.
# autoflush=False  : Flush işlemini manuel kontrol ederiz, performans kazanırız.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ---------------------------------------------------------------------------
# Declarative Base
# ---------------------------------------------------------------------------
# Tüm ORM modelleri bu Base sınıfından türeyecek.
Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency: Veritabanı Oturumu
# ---------------------------------------------------------------------------
def get_db():
    """
    FastAPI Dependency Injection için veritabanı oturumu sağlar.
    Her istek için yeni bir oturum açılır ve istek bittiğinde kapatılır.

    Kullanım (endpoint içinde):
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
