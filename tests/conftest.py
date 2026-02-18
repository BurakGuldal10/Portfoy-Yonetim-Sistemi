"""
Test Konfigürasyonu
====================
Tüm testler için kullanılacak fixtures ve ayarlar.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.database import Base
from app.main import app
from fastapi.testclient import TestClient


# Test veritabanı (SQLite in-memory)
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="function")
def db_engine():
    """Test veritabanı engine'i oluştur."""
    engine = create_engine(
        TEST_DATABASE_URL, 
        connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Her test için yeni veritabanı oturumu."""
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=db_engine
    )
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="function")
def client(db_session: Session):
    """FastAPI test client."""
    def override_get_db():
        yield db_session

    from app.database import get_db
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Test kullanıcı verileri."""
    return {
        "email": "test@example.com",
        "username": "testuser",
        "password": "test_password_123",
        "full_name": "Test User"
    }


@pytest.fixture
def test_transaction_data():
    """Test işlem verileri."""
    return {
        "stock_symbol": "THYAO",
        "stock_name": "Türk Hava Yolları",
        "transaction_type": "BUY",
        "quantity": 100,
        "price_per_unit": 245.50,
        "commission": 12.50,
        "notes": "Test işlemi"
    }
