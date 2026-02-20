"""
Auth Window - Giriş ve Kayıt Sayfaları
========================================
Modern, tasarımına dönük giriş/kayıt sayfası
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox, QStackedWidget
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QLinearGradient, QPalette

from src.api.client import APIClient, APIError


class AuthWindow(QWidget):
    """Modern tasarımlı giriş/kayıt penceresi."""

    # Signals
    login_success = pyqtSignal(str, dict)  # token, user_data
    cancel_auth = pyqtSignal()

    def __init__(self, api_client: APIClient):
        """
        Args:
            api_client: API istemcisi
        """
        super().__init__()
        self.api_client = api_client
        self.show_login = True  # Hangi sekmede olduğunu takip et
        self.init_ui()

    def init_ui(self):
        """Modern UI'yi başlat."""
        self.setWindowTitle("Portföy Yönetim Sistemi - Secure Login")
        self.setGeometry(100, 100, 900, 520)
        
        # Koyu tema - gradyan arka plan
        self.setStyleSheet("""
            QWidget {
                background-color: #050a15;
                color: #e0e7ff;
                font-family: 'Segoe UI', Arial;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Stacked widget - giriş ve kayıt sayfalarını geçiştir
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self._create_login_page())
        self.stacked_widget.addWidget(self._create_register_page())
        self.stacked_widget.setCurrentIndex(0)

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)


    def _create_login_page(self) -> QWidget:
        """Modern giriş sayfasını oluştur."""
        widget = QWidget()
        widget.setStyleSheet("background-color: #050a15;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Başlık bölümü
        title = QLabel("Geri Hoşgeldiniz")
        title_font = QFont('Segoe UI', 16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        # Açıklama
        subtitle = QLabel("Panonuza erişmek için lütfen bilgilerinizi girin")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #60a5fa; font-size: 11px;")
        layout.addWidget(subtitle)

        layout.addSpacing(15)

        # E-posta alanı
        email_label = QLabel("📧 E-posta Adresi")
        email_label.setStyleSheet("color: #93c5fd; font-weight: 500; font-size: 12px;")
        layout.addWidget(email_label)

        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("ad@sirket.com")
        self.login_email.setStyleSheet(self._get_input_stylesheet())
        layout.addWidget(self.login_email)

        # Şifre alanı
        password_label = QLabel("🔐 Şifre")
        password_label.setStyleSheet("color: #93c5fd; font-weight: 500; font-size: 13px;")
        layout.addWidget(password_label)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("••••••••")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setStyleSheet(self._get_input_stylesheet())
        layout.addWidget(self.login_password)

        # Beni Hatırla
        remember_layout = QHBoxLayout()
        self.remember_me = QCheckBox("Beni bu cihazda oturmuş tut")
        self.remember_me.setStyleSheet("""
            QCheckBox {
                color: #93c5fd;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #1e3a8a;
                border: 1px solid #1e40af;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #2563eb;
                border: 1px solid #1e40af;
                border-radius: 3px;
            }
        """)
        remember_layout.addWidget(self.remember_me)
        remember_layout.addStretch()
        layout.addLayout(remember_layout)

        layout.addSpacing(10)

        # Giriş Butonu
        login_btn = QPushButton("🔓 Panoya Giriş Yap")
        login_btn.setStyleSheet(self._get_primary_button_stylesheet())
        login_btn.setFixedHeight(40)
        login_btn.setCursor(self.cursor())
        login_btn.clicked.connect(self._handle_login)
        layout.addWidget(login_btn)

        layout.addSpacing(8)

        # Ayırıcı
        divider = QLabel("━" * 30)
        divider.setAlignment(Qt.AlignmentFlag.AlignCenter)
        divider.setStyleSheet("color: #1e3a8a;")
        layout.addWidget(divider)

        layout.addSpacing(6)

        # Kayıt sayfasına geç butonu
        register_label = QLabel("Portfolio Manager'a yeni misiniz?")
        register_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        register_label.setStyleSheet("color: #60a5fa; font-size: 11px;")
        layout.addWidget(register_label)

        register_btn = QPushButton("Güvenli Hesap Oluşturun")
        register_btn.setStyleSheet(self._get_secondary_button_stylesheet())
        register_btn.setFixedHeight(36)
        register_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        layout.addWidget(register_btn)

        layout.addSpacing(15)

        # Güvenlik bilgisi
        security_layout = QHBoxLayout()
        security_layout.setSpacing(20)
        
        ssl_label = QLabel("🔒 256-Bit SSL")
        ssl_label.setStyleSheet("color: #60a5fa; font-size: 10px; font-weight: 500;")
        security_layout.addWidget(ssl_label)

        pci_label = QLabel("✓ PCI Uyumlu")
        pci_label.setStyleSheet("color: #60a5fa; font-size: 10px; font-weight: 500;")
        security_layout.addWidget(pci_label)
        
        security_layout.addStretch()
        layout.addLayout(security_layout)

        layout.addSpacing(10)

        # Footer
        footer = QLabel("Tüm Sistemler Çalışıyor")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color: #1e40af; font-size: 11px;")
        layout.addWidget(footer)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _create_register_page(self) -> QWidget:
        """Modern kayıt sayfasını oluştur."""
        widget = QWidget()
        widget.setStyleSheet("background-color: #050a15;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Başlık
        title = QLabel("Hesap Oluştur")
        title_font = QFont('Segoe UI', 16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #ffffff;")
        layout.addWidget(title)

        # Açıklama
        subtitle = QLabel("Bize katılın ve portföyünüzü yönetmeye başlayın")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: #60a5fa; font-size: 11px;")
        layout.addWidget(subtitle)

        layout.addSpacing(12)

        # E-posta
        email_label = QLabel("📧 E-posta Adresi")
        email_label.setStyleSheet("color: #93c5fd; font-weight: 500; font-size: 13px;")
        layout.addWidget(email_label)

        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("sirket@email.com")
        self.register_email.setStyleSheet(self._get_input_stylesheet())
        layout.addWidget(self.register_email)

        # Kullanıcı Adı
        username_label = QLabel("👤 Kullanıcı Adı")
        username_label.setStyleSheet("color: #93c5fd; font-weight: 500; font-size: 13px;")
        layout.addWidget(username_label)

        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("kulldanıcıadı123")
        self.register_username.setStyleSheet(self._get_input_stylesheet())
        layout.addWidget(self.register_username)

        # Şifre
        password_label = QLabel("🔐 Şifre")
        password_label.setStyleSheet("color: #93c5fd; font-weight: 500; font-size: 13px;")
        layout.addWidget(password_label)

        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("En az 6 karakter")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.register_password.setStyleSheet(self._get_input_stylesheet())
        layout.addWidget(self.register_password)

        # Tam Ad (İsteğe bağlı)
        fullname_label = QLabel("👤 Tam Adı (İsteğe bağlı)")
        fullname_label.setStyleSheet("color: #93c5fd; font-weight: 500; font-size: 13px;")
        layout.addWidget(fullname_label)

        self.register_fullname = QLineEdit()
        self.register_fullname.setPlaceholderText("Tam adınız")
        self.register_fullname.setStyleSheet(self._get_input_stylesheet())
        layout.addWidget(self.register_fullname)

        layout.addSpacing(10)

        # Kayıt Butonu
        register_btn = QPushButton("✓ Hesap Oluştur")
        register_btn.setStyleSheet(self._get_primary_button_stylesheet())
        register_btn.setFixedHeight(40)
        register_btn.clicked.connect(self._handle_register)
        layout.addWidget(register_btn)

        layout.addSpacing(10)

        # Giriş sayfasına geç
        login_label = QLabel("Zaten bir hesabınız var mı?")
        login_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_label.setStyleSheet("color: #60a5fa; font-size: 12px;")
        layout.addWidget(login_label)

        back_btn = QPushButton("Giriş Sayfasına Dön")
        back_btn.setStyleSheet(self._get_secondary_button_stylesheet())
        back_btn.setFixedHeight(36)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn)

        layout.addSpacing(10)

        # Güvenlik bilgisi
        security_layout = QHBoxLayout()
        security_layout.setSpacing(20)
        
        ssl_label = QLabel("🔒 256-Bit SSL")
        ssl_label.setStyleSheet("color: #60a5fa; font-size: 10px; font-weight: 500;")
        security_layout.addWidget(ssl_label)

        pci_label = QLabel("✓ PCI Uyumlu")
        pci_label.setStyleSheet("color: #60a5fa; font-size: 10px; font-weight: 500;")
        security_layout.addWidget(pci_label)
        
        security_layout.addStretch()
        layout.addLayout(security_layout)

        layout.addStretch()

        widget.setLayout(layout)
        return widget

    def _get_input_stylesheet(self) -> str:
        """Input alanları için stylesheet."""
        return """
            QLineEdit {
                background-color: #0a0f1d;
                color: #e0e7ff;
                border: 1px solid #1e40af;
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 13px;
                selection-background-color: #2563eb;
            }
            QLineEdit:focus {
                border: 2px solid #2563eb;
                background-color: #0f1727;
                outline: none;
            }
            QLineEdit::placeholder {
                color: #475569;
            }
        """

    def _get_primary_button_stylesheet(self) -> str:
        """Ana buton (giriş/kayıt) için stylesheet."""
        return """
            QPushButton {
                background-color: #2563eb;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                font-weight: 600;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """

    def _get_secondary_button_stylesheet(self) -> str:
        """İkincil buton (kayıt ol / giriş yap) için stylesheet."""
        return """
            QPushButton {
                background-color: rgba(37, 99, 235, 0.1);
                color: #60a5fa;
                border: 1px solid rgba(37, 99, 235, 0.3);
                border-radius: 6px;
                font-weight: 600;
                font-size: 13px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: rgba(37, 99, 235, 0.2);
                border: 1px solid rgba(37, 99, 235, 0.5);
            }
        """

    def _handle_login(self):
        """Giriş işlemi."""
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Hata", "Tüm alanları doldurun!")
            return

        try:
            # API'ye giriş isteği gönder
            response = self.api_client.login(email, password)
            token = response.get('access_token')
            user_data = response.get('user', {})

            # Kullanıcı verilerinin doğru geldiğini kontrol et
            if not token:
                QMessageBox.critical(self, "Hata", "Giriş başarısız: Token alınamadı!")
                return
            
            if not user_data or 'id' not in user_data:
                QMessageBox.critical(self, "Hata", "Giriş başarısız: Kullanıcı bilgileri alınamadı!")
                return

            self.login_success.emit(token, user_data)
            self.clear_inputs()

        except APIError as e:
            QMessageBox.critical(self, "Giriş Hatası", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen hata: {str(e)}")

    def _handle_register(self):
        """Kayıt işlemi."""
        email = self.register_email.text().strip()
        username = self.register_username.text().strip()
        password = self.register_password.text().strip()
        fullname = self.register_fullname.text().strip()

        # Validasyon
        if not email or not username or not password:
            QMessageBox.warning(self, "Hata", "E-posta, kullanıcı adı ve şifre zorunludur!")
            return

        if len(password) < 6:
            QMessageBox.warning(self, "Hata", "Şifre en az 6 karakter olmalıdır!")
            return

        if len(username) < 3:
            QMessageBox.warning(self, "Hata", "Kullanıcı adı en az 3 karakter olmalıdır!")
            return

        try:
            # API'ye kayıt isteği gönder
            response = self.api_client.register(email, username, password, fullname)

            # Kayıt başarılı, otomatik olarak giriş yap
            QMessageBox.information(self, "Başarı", "Kayıt başarılı! Şimdi giriş yapabilirsiniz.")

            # Giriş tab'ına geç ve bilgileri doldur
            # (Bunu handle etmek için parent widget'e sinyal gönderebiliriz)

            login_response = self.api_client.login(email, password)
            token = login_response.get('access_token')
            user_data = login_response.get('user', {})

            if not token:
                QMessageBox.critical(self, "Hata", "Giriş başarısız: Token alınamadı!")
                return
            
            if not user_data or 'id' not in user_data:
                QMessageBox.critical(self, "Hata", "Giriş başarısız: Kullanıcı bilgileri alınamadı!")
                return

            self.login_success.emit(token, user_data)
            self.clear_inputs()

        except APIError as e:
            QMessageBox.critical(self, "Kayıt Hatası", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen hata: {str(e)}")

    def clear_inputs(self):
        """Tüm input alanlarını temizle."""
        self.login_email.clear()
        self.login_password.clear()
        self.register_email.clear()
        self.register_username.clear()
        self.register_password.clear()
        self.register_fullname.clear()
