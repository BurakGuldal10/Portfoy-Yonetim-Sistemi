from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QStackedWidget, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.api.client import APIClient, APIError
from src.utils.session import SessionManager


class MainWindow(QMainWindow):
    """Ana uygulama penceresi"""

    logout_requested = pyqtSignal()

    def __init__(self, api_client: APIClient, session: SessionManager):
        """
        Args:
            api_client: API istemcisi
            session: Oturum yöneticisi
        """
        print("DEBUG: MainWindow.__init__() başladı")
        super().__init__()
        print("DEBUG: super().__init__() çağrıldı")
        self.api_client = api_client
        self.session = session
        self.menu_buttons = []
        print("DEBUG: init_ui() çağrılıyor...")
        self.init_ui()
        print("DEBUG: init_ui() tamamlandı")
        # İlk sayfayı aktif et
        self._switch_page("dashboard")

    def init_ui(self):
        """UI'yi başlat - Advanced Modern Tasarım."""
        print("DEBUG: init_ui() başladı")
        self.setWindowTitle(f"Portföy Yönetim Sistemi - {self.session.get_user_username()}")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1200, 750)

        # Global stylesheet
        self.setStyleSheet(self._get_global_stylesheet())

        # Ana container
        print("DEBUG: main_container oluşturuluyor...")
        main_container = QWidget()
        print("DEBUG: main_container oluşturuldu")
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        print("DEBUG: _create_sidebar() çağrılıyor...")
        sidebar = self._create_sidebar()
        print("DEBUG: _create_sidebar() tamamlandı")
        main_layout.addWidget(sidebar, 0)

        # Ana İçerik
        content = self._create_main_content()
        main_layout.addWidget(content, 1)

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

    def _get_global_stylesheet(self) -> str:
        """Global stylesheet - Advanced Dark Theme."""
        return """
            QMainWindow, QWidget {
                background-color: #0a0e1a;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QPushButton {
                background-color: #1f2937;
                color: #ffffff;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
                font-size: 13px;
            }
            
            QPushButton:hover {
                background-color: #374151;
            }
            
            QPushButton:pressed {
                background-color: #1a1f2e;
            }
            
            QPushButton#primaryBtn {
                background-color: #3b82f6;
                color: white;
                padding: 12px 24px;
                font-weight: 600;
                font-size: 14px;
                border-radius: 10px;
            }
            
            QPushButton#primaryBtn:hover {
                background-color: #2563eb;
            }
            
            QPushButton#primaryBtn:pressed {
                background-color: #1d4ed8;
            }
            
            QPushButton#logoutBtn {
                color: #f87171;
            }
            
            QPushButton#logoutBtn:hover {
                background-color: rgba(248, 113, 113, 0.1);
            }
            
            QLineEdit, QSpinBox, QComboBox {
                background-color: rgba(255, 255, 255, 0.05);
                color: #ffffff;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 10px;
                font-size: 13px;
            }
            
            QLineEdit:focus, QSpinBox:focus, QComboBox:focus {
                border: 1px solid #3b82f6;
                background-color: rgba(255, 255, 255, 0.05);
            }
            
            QLineEdit::placeholder {
                color: #94a3b8;
            }
            
            QTableWidget {
                background-color: transparent;
                gridline-color: transparent;
                border: none;
            }
            
            QTableWidget::item {
                padding: 12px 6px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                color: #ffffff;
            }
            
            QTableWidget::item:selected {
                background-color: rgba(59, 130, 246, 0.1);
            }
            
            QHeaderView::section {
                background-color: rgba(255, 255, 255, 0.02);
                color: #94a3b8;
                padding: 12px 6px;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                font-weight: 600;
                font-size: 11px;
            }
            
            QScrollBar:vertical {
                background-color: transparent;
                width: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #1e293b;
                border-radius: 3px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #334155;
            }
            
            QComboBox::drop-down {
                border: none;
            }
        """

    def _create_sidebar(self) -> QWidget:
        """Sidebar oluştur - Daha kompakt ve narin tasarım."""
        sidebar = QWidget()
        sidebar.setFixedWidth(190)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #0d1326;
                border-right: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(0)

        # Logo ve Brand
        logo_container = QHBoxLayout()
        logo_container.setSpacing(8)
        
        logo_btn = QPushButton("N")
        logo_btn.setFixedSize(26, 26)
        logo_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
        """)
        logo_container.addWidget(logo_btn)
        
        brand_label = QLabel("Finansal")
        brand_font = QFont('Segoe UI', 11, QFont.Weight.Bold)
        brand_label.setFont(brand_font)
        logo_container.addWidget(brand_label)
        logo_container.addStretch()
        
        layout.addLayout(logo_container)
        layout.addSpacing(15)

        # Menü öğeleri
        menu_items = [
            ("📊", "Dashboard", "dashboard"),
            ("✓", "İşlemler", "transactions"),
            ("🕐", "İşlem Geçmişi", "transaction_history"),
            ("➕", "Yeni İşlem", "new_transaction"),
            ("📈", "Raporlar", "reports"),
            ("⚙️", "Ayarlar", "settings"),
        ]

        for icon, text, page_id in menu_items:
            btn = QPushButton(f"{icon}  {text}")
            btn.setFixedHeight(48)
            btn.setProperty("page_id", page_id)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: rgba(255, 255, 255, 0.6);
                    border: none;
                    border-radius: 6px;
                    padding: 12px 14px;
                    text-align: left;
                    font-weight: 500;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.05);
                    color: white;
                }
                QPushButton[active="true"] {
                    background-color: rgba(59, 130, 246, 0.12);
                    color: #3b82f6;
                    border-left: 2px solid #3b82f6;
                }
            """)
            btn.clicked.connect(lambda checked, pid=page_id: self._switch_page(pid))
            self.menu_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        # Çıkış butonu
        logout_btn = QPushButton("➔  Çıkış")
        logout_btn.setFixedHeight(48)
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #f87171;
                border: none;
                border-radius: 6px;
                padding: 12px 14px;
                text-align: left;
                font-weight: 500;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(248, 113, 113, 0.08);
                color: #fca5a5;
            }
        """)
        logout_btn.clicked.connect(self._handle_logout)
        layout.addWidget(logout_btn)

        sidebar.setLayout(layout)
        return sidebar

    def _create_main_content(self) -> QWidget:
        """Ana içerik alanı oluştur."""
        print("DEBUG: _create_main_content() başladı")
        # Pages import'ını burada yapıyoruz (QApplication'dan sonra)
        print("DEBUG: Pages import ediliyor...")
        from src.ui.pages import DashboardPage, TransactionHistoryPage, PlaceholderPage
        print("DEBUG: Pages import edildi")
        
        content = QWidget()
        print("DEBUG: content widget oluşturuldu")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        print("DEBUG: _create_header() çağrılıyor...")
        header = self._create_header()
        print("DEBUG: _create_header() tamamlandı")
        layout.addWidget(header, 0)

        # Stacked widget for pages
        self.stacked_widget = QStackedWidget()
        
        # Dashboard sayfası
        print("DEBUG: DashboardPage oluşturuluyor...")
        dashboard_page = DashboardPage(self.api_client, self.session)
        print("DEBUG: DashboardPage oluşturuldu")
        self.stacked_widget.addWidget(dashboard_page)
        
        # İşlem Geçmişi sayfası
        print("DEBUG: TransactionHistoryPage oluşturuluyor...")
        history_page = TransactionHistoryPage(self.api_client)
        print("DEBUG: TransactionHistoryPage oluşturuldu")
        self.stacked_widget.addWidget(history_page)
        
        # Placeholder sayfalar (diğer sayfalar için)
        placeholder_messages = [
            "İşlemler sayfası yakında eklenecek",
            "Yeni İşlem sayfası yakında eklenecek",
            "Raporlar sayfası yakında eklenecek",
            "Ayarlar sayfası yakında eklenecek"
        ]
        print("DEBUG: Placeholder sayfaları oluşturuluyor...")
        for msg in placeholder_messages:
            placeholder_page = PlaceholderPage(msg)
            self.stacked_widget.addWidget(placeholder_page)
        print("DEBUG: Placeholder sayfaları oluşturuldu")
        
        layout.addWidget(self.stacked_widget, 1)

        content.setLayout(layout)
        return content
    
    def _switch_page(self, page_id: str):
        """Sayfa değiştir ve menü butonlarını güncelle."""
        page_map = {
            "dashboard": 0,
            "transactions": 2,  # Placeholder (İşlemler)
            "transaction_history": 1,  # İşlem Geçmişi
            "new_transaction": 3,
            "reports": 4,
            "settings": 5,
        }
        
        if page_id in page_map:
            self.stacked_widget.setCurrentIndex(page_map[page_id])
            
            # Menü butonlarını güncelle
            for btn in self.menu_buttons:
                if btn.property("page_id") == page_id:
                    btn.setProperty("active", True)
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)
                else:
                    btn.setProperty("active", False)
                    btn.style().unpolish(btn)
                    btn.style().polish(btn)

    def _create_header(self) -> QWidget:
        """Header oluştur - Daha narin ve kompakt."""
        header = QFrame()
        header.setFixedHeight(50)
        header.setStyleSheet("""
            QFrame {
                background-color: rgba(10, 14, 26, 0.9);
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(20, 0, 20, 0)

        # Sol taraf - Hoşgeldiniz
        left_layout = QVBoxLayout()
        left_layout.setSpacing(0)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        welcome_label = QLabel(f"Hoşgeldiniz, {self.session.get_user_username()} 👋")
        welcome_font = QFont('Segoe UI', 11, QFont.Weight.Bold)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #ffffff;")

        left_layout.addWidget(welcome_label)
        layout.addLayout(left_layout, 1)

        # Sağ taraf - Butonlar
        right_layout = QHBoxLayout()
        right_layout.setSpacing(12)

        # Bildirim butonu
        notification_btn = QPushButton("🔔")
        notification_btn.setFixedSize(30, 30)
        notification_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
            }
        """)
        right_layout.addWidget(notification_btn)

        # Profil bölümü
        profile_layout = QHBoxLayout()
        profile_layout.setSpacing(6)
        profile_layout.setContentsMargins(0, 0, 0, 0)
        
        profile_label = QLabel(self.session.get_user_username())
        profile_label.setFont(QFont('Segoe UI', 9))
        profile_layout.addWidget(profile_label)
        
        avatar_label = QLabel("👤")
        avatar_label.setStyleSheet("font-size: 14px;")
        profile_layout.addWidget(avatar_label)

        right_layout.addLayout(profile_layout)
        layout.addLayout(right_layout)

        header.setLayout(layout)
        return header

    def _handle_logout(self):
        """Çıkış."""
        reply = QMessageBox.question(
            self, "Onay",
            "Çıkış yapmak istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.session.logout()
            self.logout_requested.emit()
