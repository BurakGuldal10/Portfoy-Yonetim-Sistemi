"""
Auth Service - Kimlik Doğrulama İş Mantığı
=============================================
Kullanıcı kayıt ve giriş işlemlerinin iş mantığını yönetir.
Router'dan bağımsız tutularak test edilebilirliği artırır.
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password, create_access_token
from app.logger import get_logger

logger = get_logger(__name__)


def register_user(db: Session, user_data: UserCreate) -> User:
    """
    Yeni kullanıcı kaydı oluşturur.

    Adımlar:
        1. E-posta adresinin daha önce kullanılmadığını kontrol et
        2. Kullanıcı adının benzersiz olduğunu kontrol et
        3. Şifreyi hashle
        4. Kullanıcıyı veritabanına kaydet

    Args:
        db: Veritabanı oturumu
        user_data: Kullanıcı kayıt verileri (email, username, password, full_name)

    Returns:
        Oluşturulan User nesnesi

    Raises:
        HTTPException 400: E-posta veya kullanıcı adı zaten kullanılıyorsa
    """
    # Şifre uzunluğu kontrolü (bcrypt max 72 bytes)
    if len(user_data.password.encode('utf-8')) > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Şifre 72 karakterden daha kısa olmalıdır.",
        )
    
    # E-posta kontrolü (güvenlik: bilgi sızıntısını önlemek için genel hata mesajı)
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        logger.warning(f"📧 Kayıt hatası: E-posta zaten var: {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kayıt işlemi başarısız oldu. Lütfen verilerinizi kontrol edin.",
        )

    # Kullanıcı adı kontrolü
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_username:
        logger.warning(f"👤 Kayıt hatası: Username zaten var: {user_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kayıt işlemi başarısız oldu. Lütfen verilerinizi kontrol edin.",
        )

    # Yeni kullanıcı oluştur
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"✅ Yeni kullanıcı kaydedildi: {new_user.username} ({new_user.email})")
    return new_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Kullanıcı kimliğini doğrular (giriş işlemi).

    Adımlar:
        1. E-posta ile kullanıcıyı bul
        2. Şifreyi doğrula
        3. Hesabın aktif olduğunu kontrol et

    Args:
        db: Veritabanı oturumu
        email: Kullanıcının e-posta adresi
        password: Kullanıcının girdiği şifre

    Returns:
        Doğrulanmış User nesnesi

    Raises:
        HTTPException 401: E-posta veya şifre yanlışsa
        HTTPException 403: Hesap devre dışıysa
    """
    # Şifre uzunluğu kontrolü (bcrypt max 72 bytes)
    if len(password.encode('utf-8')) > 72:
        logger.warning(f"🔒 Başarısız giriş denemesi: Çok uzun şifre - {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()

    # Kullanıcı bulunamadı veya şifre yanlış
    # Not: Güvenlik açısından aynı hata mesajı verilir (bilgi sızıntısını önler)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning(f"🔒 Başarısız giriş denemesi: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-posta veya şifre hatalı.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Hesap aktiflik kontrolü
    if not user.is_active:
        logger.warning(f"⛔ Devre dışı hesaba giriş denemesi: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu hesap devre dışı bırakılmış.",
        )

    logger.info(f"✅ Başarılı giriş: {user.username} ({email})")
    return user


def generate_token_for_user(user: User) -> str:
    """
    Kullanıcı için JWT access token oluşturur.

    Args:
        user: Doğrulanmış kullanıcı nesnesi

    Returns:
        JWT token string'i
    """
    token_data = {"sub": user.email}
    return create_access_token(data=token_data)
