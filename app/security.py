"""
Güvenlik Modülü (Security)
============================
JWT token oluşturma, doğrulama ve şifre hashleme işlemlerini yönetir.
Bu modül auth endpointlerinden bağımsızdır ve tüm güvenlik mantığını
merkezi bir yerde tutar.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

# ---------------------------------------------------------------------------
# Şifre Hashleme Ayarları
# ---------------------------------------------------------------------------
# bcrypt: Endüstri standardı şifre hashleme algoritması
# deprecated="auto": Eski hash formatlarını otomatik olarak günceller
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------------------------------------------------------------------------
# OAuth2 Token URL
# ---------------------------------------------------------------------------
# tokenUrl: Login endpointinin yolu (Swagger UI için gerekli)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ===========================================================================
# ŞİFRE İŞLEMLERİ
# ===========================================================================

def hash_password(password: str) -> str:
    """
    Düz metin şifreyi hashler.

    Args:
        password: Kullanıcının girdiği düz metin şifre

    Returns:
        Hashlenmiş şifre string'i
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Düz metin şifreyi, hashlenmiş şifre ile karşılaştırır.

    Args:
        plain_password: Kullanıcının girdiği şifre
        hashed_password: Veritabanındaki hashlenmiş şifre

    Returns:
        True: Şifre doğru / False: Şifre yanlış
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===========================================================================
# JWT TOKEN İŞLEMLERİ
# ===========================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT access token oluşturur.

    Args:
        data: Token payload'ına eklenecek veriler (genellikle {"sub": user_email})
        expires_delta: Token geçerlilik süresi (varsayılan: config'den okunur)

    Returns:
        Kodlanmış JWT token string'i
    """
    to_encode = data.copy()

    # Token süresini belirle
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})

    # Token'ı oluştur ve döndür
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


def verify_token(token: str) -> dict:
    """
    JWT token'ı doğrular ve payload'ı döndürür.

    Args:
        token: Doğrulanacak JWT token

    Returns:
        Token payload'ı (dict)

    Raises:
        HTTPException: Token geçersizse veya süresi dolmuşsa
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token doğrulanamadı. Lütfen tekrar giriş yapın.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        raise credentials_exception


# ===========================================================================
# MEVCUT KULLANICI DOĞRULAMA (Dependency)
# ===========================================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency: Mevcut oturum açmış kullanıcıyı döndürür.

    Bu fonksiyon, korunan endpointlerde kullanılır:
        @router.get("/protected")
        def protected_route(current_user: User = Depends(get_current_user)):
            ...

    İşleyiş:
        1. Authorization header'dan Bearer token'ı alır
        2. Token'ı doğrular
        3. Token'daki email ile kullanıcıyı veritabanından bulur
        4. Kullanıcı nesnesi döndürür

    Raises:
        HTTPException 401: Token geçersizse veya kullanıcı bulunamazsa
    """
    from app.models.user import User  # Circular import'u önlemek için burada import

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kimlik doğrulanamadı.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Token'ı doğrula
    payload = verify_token(token)
    email: str = payload.get("sub")

    if email is None:
        raise credentials_exception

    # Kullanıcıyı veritabanından bul
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu hesap devre dışı bırakılmış.",
        )

    return user
