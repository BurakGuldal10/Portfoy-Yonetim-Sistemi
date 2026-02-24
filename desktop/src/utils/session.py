"""
Utilities - Session, Token ve yardımcı fonksiyonlar
====================================================
"""

import json
import os
from pathlib import Path
from typing import Optional


class SessionManager:
    """Kullanıcı oturumunu yönetir (token ve kullanıcı bilgileri)."""

    def __init__(self, config_dir: str = None):
        """
        Args:
            config_dir: Konfigürasyon dosyalarının bulunacağı dizin
        """
        if config_dir is None:
            # Windows: AppData\Local, Mac: ~/.config, Linux: ~/.config
            if os.name == 'nt':
                config_dir = os.path.join(os.getenv('APPDATA'), 'PortfoyYonetim')
            else:
                config_dir = os.path.join(os.path.expanduser('~'), '.config', 'portfoy_yonetim')

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.config_dir / 'session.json'

        self.token: Optional[str] = None
        self.user_data: dict = {}

        # Kaydedilmiş oturumu yükle
        self._load_session()

    def _load_session(self):
        """Kaydedilmiş oturumu dosyadan yükle."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.token = data.get('token')
                    self.user_data = data.get('user_data', {})
                    # Verinin doğru geldiğini kontrol et
                    if not self.token or not self.user_data:
                        self._clear_session()
                    else:
                        print(f"[OK] Oturum başarıyla yüklendi. Kullanıcı: {self.get_user_username()}")
            except Exception as e:
                print(f"[HATA] Oturum yükleme hatası: {e}")
                self._clear_session()
    
    def _clear_session(self):
        """Oturum verilerini sıfırla."""
        self.token = None
        self.user_data = {}

    def _save_session(self):
        """Oturumu dosyaya kaydet."""
        try:
            data = {
                'token': self.token,
                'user_data': self.user_data,
            }
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Oturum kaydetme hatası: {e}")

    def login(self, token: str, user_data: dict):
        """Oturum başlat."""
        self.token = token
        self.user_data = user_data
        self._save_session()
        print(f"[OK] Oturum başlatıldı. Kullanıcı: {self.get_user_username()}")

    def logout(self):
        """Oturumu bitir."""
        username = self.get_user_username()
        self.token = None
        self.user_data = {}
        self._save_session()
        if self.session_file.exists():
            self.session_file.unlink()
        print(f"[OK] Oturum sonlandırıldı. Kullanıcı: {username}")

    def is_logged_in(self) -> bool:
        """Kullanıcı giriş yapmış mı?"""
        return self.token is not None

    def get_user_username(self) -> str:
        """Kullanıcı adını al."""
        # Önce username'i kontrol et, yoksa full_name'i, yoksa email'i, en son bilinmeyen
        username = self.user_data.get('username')
        if username:
            return username
        
        full_name = self.user_data.get('full_name')
        if full_name:
            return full_name
        
        email = self.user_data.get('email')
        if email:
            return email
        
        return 'Kullanıcı'

    def get_user_email(self) -> str:
        """Kullanıcı e-postasını al."""
        return self.user_data.get('email', 'Unknown')
    
    def get_user_data(self) -> dict:
        """Tüm kullanıcı verilerini al."""
        return self.user_data.copy()

    def get_token(self) -> Optional[str]:
        """Token'ı al."""
        return self.token


class AppSettings:
    """Uygulama ayarları."""

    def __init__(self, config_dir: str = None):
        """
        Args:
            config_dir: Ayarlar dosyasının bulunacağı dizin
        """
        if config_dir is None:
            if os.name == 'nt':
                config_dir = os.path.join(os.getenv('APPDATA'), 'PortfoyYonetim')
            else:
                config_dir = os.path.join(os.path.expanduser('~'), '.config', 'portfoy_yonetim')

        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = self.config_dir / 'settings.json'

        # Varsayılan ayarlar
        self.defaults = {
            'api_url': 'http://localhost:8000',
            'theme': 'light',  # light, dark
            'page_size': 20,
            'auto_refresh': True,
            'refresh_interval': 5,  # saniye
        }

        self.settings = self.defaults.copy()
        self._load_settings()

    def _load_settings(self):
        """Kaydedilmiş ayarları yükle."""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except Exception as e:
                print(f"Ayarlar yükleme hatası: {e}")

    def _save_settings(self):
        """Ayarları dosyaya kaydet."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Ayarlar kaydetme hatası: {e}")

    def get(self, key: str, default=None):
        """Ayar değerini al."""
        return self.settings.get(key, default)

    def set(self, key: str, value):
        """Ayar değerini ayarla."""
        self.settings[key] = value
        self._save_settings()

    def get_api_url(self) -> str:
        """API URL'sini al."""
        return self.get('api_url', self.defaults['api_url'])

    def set_api_url(self, url: str):
        """API URL'sini ayarla."""
        self.set('api_url', url)

    def get_theme(self) -> str:
        """Tema al."""
        return self.get('theme', self.defaults['theme'])

    def set_theme(self, theme: str):
        """Tema ayarla."""
        if theme in ['light', 'dark']:
            self.set('theme', theme)
