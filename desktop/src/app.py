"""
Application - Ana Uygulama Sınıfı
==================================
"""

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer

from src.api.client import APIClient, APIError
from src.utils.session import SessionManager, AppSettings


class Application:
    """Masaüstü uygulaması ana sınıfı."""

    def __init__(self, q_app: QApplication):
        """Uygulamayı başlat."""
        self.app = q_app
        self.session = SessionManager()
        self.settings = AppSettings()
        self.api_client = APIClient(self.settings.get_api_url())

        self.auth_window = None
        self.main_window = None

    def run(self):
        """Uygulamayı çalıştır."""
        print("DEBUG: Uygulama başladı")
        print(f"DEBUG: Session logged in: {self.session.is_logged_in()}")
        
        if self.session.is_logged_in():
            # Kaydedilmiş oturum varsa, API token'ını ayarla
            self.api_client.set_token(self.session.get_token())
            self._show_main_window()
        else:
            # Kimlik doğrulama penceresini aç
            print("DEBUG: Auth window gösteriliyor...")
            self._show_auth_window()
            print("DEBUG: Auth window gösterildi, event loop başlatılıyor...")

        print("DEBUG: app.exec() çağrılıyor...")
        return self.app.exec()

    def _show_auth_window(self):
        """Kimlik doğrulama penceresini göster."""
        from src.ui.auth_window import AuthWindow
        
        if self.main_window:
            self.main_window.close()

        self.auth_window = AuthWindow(self.api_client)
        self.auth_window.login_success.connect(self._handle_login_success)
        self.auth_window.cancel_auth.connect(self.app.quit)
        self.auth_window.show()
        
        # Backend'i arkaplanda kontrol et (health check)
        QTimer.singleShot(1000, self._check_backend_health)

    def _show_main_window(self):
        """Ana pencereyi göster."""
        from src.ui.main_window import MainWindow
        
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
    
    def _check_backend_health(self):
        """Backend'in sağlık durumunu kontrol et (arkaplanda)."""
        try:
            self.api_client.health_check()
        except APIError as e:
            # Giriş penceresinde uyarı göster
            if self.auth_window and self.auth_window.isVisible():
                QMessageBox.warning(
                    self.auth_window, "Uyarı",
                    f"⚠️ Backend bağlantısı sorunu:\n\n{str(e)}\n\n"
                    f"API URL: {self.api_client.base_url}"
                )


def main():
    """Uygulamayı başlat (main.py tarafından kullanılan legacy fonksiyon)."""
    from PyQt6.QtWidgets import QApplication
    
    try:
        # QApplication'ı ÖNCE oluştur, diğer şeylerden önce
        q_app = QApplication([])
        app = Application(q_app)
        exit_code = app.run()
        return exit_code
    except Exception as e:
        print(f"Application error: {e}", file=__import__('sys').stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    main()
