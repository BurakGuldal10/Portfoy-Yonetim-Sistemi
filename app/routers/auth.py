"""
Auth Router - Kimlik Doğrulama Endpointleri
=============================================
Kullanıcı kayıt (register) ve giriş (login) endpointlerini tanımlar.
İş mantığı auth_service.py'de yer alır, burada sadece HTTP katmanı yönetilir.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_token_for_user,
)
from app.security import get_current_user
from app.models.user import User

# Router tanımı
router = APIRouter(
    prefix="/api/auth",
    tags=["Kimlik Doğrulama (Auth)"],
)


# ===========================================================================
# POST /api/auth/register - Kullanıcı Kaydı
# ===========================================================================
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni kullanıcı kaydı",
    description="E-posta, kullanıcı adı ve şifre ile yeni bir hesap oluşturur.",
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Yeni kullanıcı kaydı oluşturur.

    - **email**: Benzersiz e-posta adresi
    - **username**: Benzersiz kullanıcı adı (min 3 karakter)
    - **password**: Şifre (min 6 karakter)
    - **full_name**: Tam ad (opsiyonel)
    """
    new_user = register_user(db, user_data)
    return new_user


# ===========================================================================
# POST /api/auth/login - Kullanıcı Girişi
# ===========================================================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Kullanıcı girişi",
    description="E-posta ve şifre ile giriş yaparak JWT token alır.",
)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Kullanıcı girişi yapar ve JWT access token döndürür.

    Swagger UI'da test edebilmek için OAuth2PasswordRequestForm kullanılır.
    - **username**: Aslında e-posta adresidir (OAuth2 standardı "username" der)
    - **password**: Kullanıcı şifresi
    """
    # OAuth2 standardı "username" alanını kullanır, biz email olarak kullanıyoruz
    user = authenticate_user(db, email=form_data.username, password=form_data.password)
    token = generate_token_for_user(user)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


# ===========================================================================
# GET /api/auth/me - Mevcut Kullanıcı Bilgisi
# ===========================================================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Mevcut kullanıcı bilgisi",
    description="JWT token ile kimliği doğrulanmış kullanıcının bilgilerini döndürür.",
)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Giriş yapmış kullanıcının profil bilgilerini döndürür.

    Bu endpoint korumalıdır - geçerli bir Bearer token gerektirir.
    """
    return current_user
