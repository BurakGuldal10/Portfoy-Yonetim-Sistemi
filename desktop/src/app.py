"""
Application - Ana Uygulama Sınıfı
==================================
"""

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

from src.api.client import APIClient, APIError
from src.ui.auth_window import AuthWindow
from src.ui.main_window import MainWindow
from src.utils.session import SessionManager, AppSettings


class Application:
    """Masaüstü uygulaması ana sınıfı."""

    def __init__(self):
        """Uygulamayı başlat."""
        self.app = QApplication([])
        self.session = SessionManager()
        self.settings = AppSettings()
        self.api_client = APIClient(self.settings.get_api_url())

        self.auth_window = None
        self.main_window = None

    def run(self):
        """Uygulamayı çalıştır."""
        if self.session.is_logged_in():
            # Kaydedilmiş oturum varsa, API token'ını ayarla
            self.api_client.set_token(self.session.get_token())
            self._show_main_window()
        else:
            # Kimlik doğrulama penceresini aç
            self._show_auth_window()

        return self.app.exec()

    def _show_auth_window(self):
        """Kimlik doğrulama penceresini göster."""
        try:
            self.api_client.health_check()
        except APIError:
            QMessageBox.critical(
                None, "Hata",
                "🔴 API sunucusuna bağlanılamadı.\n\n"
                "Lütfen API sunucusunun çalıştığını ve doğru adreste olduğunu kontrol edin.\n"
                f"API URL: {self.api_client.base_url}"
            )
            return

        if self.main_window:
            self.main_window.close()

        self.auth_window = AuthWindow(self.api_client)
        self.auth_window.login_success.connect(self._handle_login_success)
        self.auth_window.cancel_auth.connect(self.app.quit)
        self.auth_window.show()

    def _show_main_window(self):
        """Ana pencereyi göster."""
        if self.auth_window:
            self.auth_window.close()

        self.main_window = MainWindow(self.api_client, self.session)
        self.main_window.logout_requested.connect(self._show_auth_window)
        self.main_window.show()

    def _handle_login_success(self, token: str, user_data: dict):
        """Başarılı giriş sonrası."""
        # Oturumu kaydet
        self.api_client.set_token(token)
        self.session.login(token, user_data)
        
        # Oturum verilerinin doğru kaydedildiğini kontrol et
        if not self.session.is_logged_in():
            QMessageBox.critical(
                None, "Hata",
                "Oturum kaydedilemedi. Lütfen tekrar deneyin."
            )
            return

        # Ana pencereyi göster
        self._show_main_window()


def main():
    """Uygulamayı başlat."""
    app = Application()
    exit_code = app.run()
    return exit_code


if __name__ == '__main__':
    main()
