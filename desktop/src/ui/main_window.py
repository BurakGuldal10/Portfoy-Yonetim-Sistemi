"""
Main Window - Ana Uygulama Penceresi (Yeni Tasarım)
======================================================
Modern, profesyonel finans dashboard'u
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
    QLineEdit, QComboBox, QDoubleSpinBox, QDateTimeEdit,
    QTextEdit, QHeaderView, QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QDateTime, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QColor, QIcon, QPixmap, QBrush
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime, timedelta

from src.api.client import APIClient, APIError
from src.models.data_models import Transaction
from src.utils.session import SessionManager



class MainWindow(QMainWindow):
    """Ana uygulama penceresi - Modern Dashboard."""

    logout_requested = pyqtSignal()

    def __init__(self, api_client: APIClient, session: SessionManager):
        """
        Args:
            api_client: API istemcisi
            session: Oturum yöneticisi
        """
        super().__init__()
        self.api_client = api_client
        self.session = session
        self.transactions = []
        self.portfolio_summary = None

        self.init_ui()
        self.load_data()

    def init_ui(self):
        """UI'yi başlat - Modern Tasarım."""
        self.setWindowTitle(f"Portföy Yönetim Sistemi - {self.session.get_user_username()}")
        self.setGeometry(100, 100, 1600, 900)

        # Koyu tema stylesheet
        self.setStyleSheet(self._get_global_stylesheet())

        # Ana container
        main_container = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Sol Sidebar
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar, 0)

        # Ana İçerik
        content = self._create_content()
        main_layout.addWidget(content, 1)

        main_container.setLayout(main_layout)
        self.setCentralWidget(main_container)

    def _get_global_stylesheet(self) -> str:
        """Global stylesheet - Koyu tema (HTML/CSS'den uyarlanmış)."""
        return """
            QWidget {
                background-color: #0f172a;
                color: #ffffff;
                font-family: Arial, sans-serif;
            }
            
            QMainWindow {
                background-color: #0f172a;
            }
            
            QPushButton {
                background-color: #1f2937;
                color: #ffffff;
                border: none;
                border-radius: 6px;
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
                border: none;
                padding: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            
            QPushButton#primaryBtn:hover {
                background-color: #2563eb;
            }
            
            QLineEdit, QDoubleSpinBox, QDateTimeEdit, QComboBox, QSpinBox {
                background-color: #1e293b;
                color: #ffffff;
                border: 1px solid #374151;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
            
            QLineEdit:focus, QDoubleSpinBox:focus, QDateTimeEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3b82f6;
                background-color: #1e293b;
                color: #ffffff;
            }
            
            QLineEdit::placeholder {
                color: #9ca3af;
            }
            
            QComboBox::drop-down {
                border: none;
            }
            
            QComboBox::down-arrow {
                color: #9ca3af;
            }
            
            QTableWidget {
                background-color: #1e293b;
                gridline-color: #374151;
                border: none;
                border-radius: 10px;
            }
            
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #374151;
            }
            
            QTableWidget::item:selected {
                background-color: #334155;
            }
            
            QHeaderView::section {
                background-color: #1e293b;
                color: #9ca3af;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #374151;
                font-weight: 600;
                font-size: 12px;
            }
            
            QScrollBar:vertical {
                background-color: #0f172a;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #374151;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #4b5563;
            }
        """

    def _create_sidebar(self) -> QWidget:
        """Sol sidebar menüsü oluştur (HTML tasarımı)."""
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #111827;
                border-right: 1px solid #1f2937;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        # Logo/Brand
        logo_label = QLabel("N")
        logo_font = QFont('Arial', 20, QFont.Weight.Bold)
        logo_label.setFont(logo_font)
        logo_label.setStyleSheet("color: #ffffff; margin-bottom: 30px;")
        layout.addWidget(logo_label)

        layout.addSpacing(10)

        # Menü butonları
        menu_items = [
            "Dashboard",
            "İşlemler",
            "Yeni İşlem",
            "Ayarlar",
            "Çıkış",
        ]

        for menu_text in menu_items:
            btn = QPushButton(menu_text)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: transparent;
                    color: #ffffff;
                    border: none;
                    padding: 12px;
                    text-align: left;
                    font-weight: 400;
                    font-size: 13px;
                    border-radius: 6px;
                }}
                QPushButton:hover {{
                    background-color: #1f2937;
                }}
            """)
            
            if menu_text == "Çıkış":
                btn.clicked.connect(self._handle_logout)
            
            layout.addWidget(btn)

        layout.addStretch()

        sidebar.setLayout(layout)
        return sidebar

    def _create_content(self) -> QWidget:
        """Ana içerik alanını oluştur."""
        content = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(30)

        # Üst bar (Hoşgeldiniz + İstatistik)
        top_bar = self._create_top_bar()
        layout.addLayout(top_bar)

        # Özet kardları
        summary_cards = self._create_summary_cards()
        layout.addLayout(summary_cards)

        # Ana içerik (Sol: Grafik + Tablo, Sağ: Hızlı İşlem)
        main_content = self._create_main_content()
        layout.addLayout(main_content, 1)

        content.setLayout(layout)
        return content

    def _create_top_bar(self) -> QHBoxLayout:
        """Üst bar - Hoşgeldiniz ve istatistikler."""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sol taraf: Hoşgeldiniz + Açıklama
        left_layout = QVBoxLayout()

        welcome_label = QLabel(f"Hoşgeldiniz, {self.session.get_user_username()} 👋")
        welcome_font = QFont('Segoe UI', 18, QFont.Weight.Bold)
        welcome_label.setFont(welcome_font)
        welcome_label.setStyleSheet("color: #f3f4f6;")

        today_label = QLabel("Bugün portföyünüz %1.23 arttı")
        today_font = QFont('Segoe UI', 12)
        today_label.setFont(today_font)
        today_label.setStyleSheet("color: #9ca3af;")

        left_layout.addWidget(welcome_label)
        left_layout.addWidget(today_label)

        layout.addLayout(left_layout, 1)

        # Sağ taraf: Bildirim + Profil
        refresh_btn = QPushButton("🔄")
        refresh_btn.setFixedSize(40, 40)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2d5a8c;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        layout.addWidget(refresh_btn)

        notification_btn = QPushButton("🔔")
        notification_btn.setFixedSize(40, 40)
        notification_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2d5a8c;
            }
        """)
        layout.addWidget(notification_btn)

        profile_btn = QPushButton("👤 " + self.session.get_user_username())
        profile_btn.setFixedHeight(40)
        profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e3a5f;
                border: none;
                border-radius: 6px;
                padding: 0px 15px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2d5a8c;
            }
        """)
        layout.addWidget(profile_btn)

        return layout

    def _create_summary_cards(self) -> QHBoxLayout:
        """4 özet kartı oluştur (HTML tasarımı)."""
        layout = QHBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(0, 0, 0, 0)

        # Toplam Portföy
        card1 = self._create_card(
            "Toplam Portföy",
            "24,350 TL"
        )
        layout.addWidget(card1)

        # Günlük Kar/Zarar
        card2 = self._create_card(
            "Günlük Kar/Zarar",
            "+450 TL",
            is_positive=True
        )
        layout.addWidget(card2)

        # Toplam Hisse
        card3 = self._create_card(
            "Toplam Hisse",
            "7"
        )
        layout.addWidget(card3)

        # Toplam Komisyon
        card4 = self._create_card(
            "Toplam Komisyon",
            "125 TL"
        )
        layout.addWidget(card4)

        return layout

    def _create_card(self, title: str, value: str, color: str = None, is_positive: bool = False) -> QWidget:
        """Özet kartı oluştur (HTML tasarımı)."""
        card = QFrame()
        card.setFixedHeight(100)
        card.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık
        title_label = QLabel(title)
        title_font = QFont('Arial', 12)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #9ca3af;")

        # Değer
        value_label = QLabel(value)
        value_font = QFont('Arial', 22, QFont.Weight.Bold)
        value_label.setFont(value_font)
        
        if is_positive:
            value_label.setStyleSheet("color: #22c55e;")
        else:
            value_label.setStyleSheet("color: #ffffff;")

        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addStretch()

        card.setLayout(layout)
        return card

    def _create_main_content(self) -> QHBoxLayout:
        """Ana içerik: Sol (grafik + tablo) + Sağ (hızlı işlem)."""
        layout = QHBoxLayout()
        layout.setSpacing(20)

        # Sol taraf (70%)
        left_layout = QVBoxLayout()
        left_layout.setSpacing(20)

        # Grafik
        chart_widget = self._create_portfolio_chart()
        left_layout.addWidget(chart_widget, 1)

        # Portföy tablosu
        table_widget = self._create_portfolio_table()
        left_layout.addWidget(table_widget, 1)

        left_container = QWidget()
        left_container.setLayout(left_layout)
        layout.addWidget(left_container, 7)

        # Sağ taraf (30%) - Hızlı İşlem
        quick_trade = self._create_quick_trade_panel()
        layout.addWidget(quick_trade, 3)

        return layout

    def _create_portfolio_chart(self) -> QWidget:
        """Portföy değer değişimi grafiği (HTML tasarımı)."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık
        title_label = QLabel("Portföy Değer Değişimi")
        title_font = QFont('Arial', 13, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)

        layout.addSpacing(15)

        # Matplotlib grafik
        try:
            figure = Figure(figsize=(10, 3.5), dpi=100, facecolor='#1e293b', edgecolor='none')
            figure.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.1)
            ax = figure.add_subplot(111)
            ax.set_facecolor('#1e293b')

            # Örnek veri
            dates = list(range(30))
            values = [20000 + i * 100 + (i % 3) * 200 for i in dates]

            ax.plot(dates, values, color='#22c55e', linewidth=2.5, marker='o', markersize=4, markerfacecolor='#22c55e')
            ax.fill_between(dates, values, alpha=0.15, color='#22c55e')
            ax.grid(True, alpha=0.15, color='#374151', linestyle='-', linewidth=0.5)
            ax.set_xlabel('')
            ax.set_ylabel('')
            
            # Eksenleri uyarla
            for label in ax.get_xticklabels():
                label.set_color('#9ca3af')
                label.set_fontsize(9)
            for label in ax.get_yticklabels():
                label.set_color('#9ca3af')
                label.set_fontsize(9)

            ax.spines['left'].set_color('#374151')
            ax.spines['bottom'].set_color('#374151')
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            canvas = FigureCanvas(figure)
            canvas.setMinimumHeight(220)
            layout.addWidget(canvas)
        except Exception as e:
            error_label = QLabel(f"Grafik yüklenemedi: {str(e)}")
            error_label.setStyleSheet("color: #9ca3af; padding: 50px;")
            layout.addWidget(error_label)

        widget.setLayout(layout)
        return widget

    def _create_portfolio_table(self) -> QWidget:
        """Portföy tablosu (HTML tasarımı)."""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık
        title_label = QLabel("Portföy Özeti")
        title_font = QFont('Arial', 13, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)

        layout.addSpacing(15)

        # Tablo
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(5)
        self.portfolio_table.setHorizontalHeaderLabels([
            "Hisse", "Adet", "Ortalama", "Toplam", "Kar/Zarar"
        ])
        self.portfolio_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.portfolio_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.portfolio_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.portfolio_table.setAlternatingRowColors(False)
        self.portfolio_table.setShowGrid(False)
        self.portfolio_table.verticalHeader().setVisible(False)
        self.portfolio_table.setMaximumHeight(250)

        # Tablo CSS
        self.portfolio_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                gridline-color: transparent;
                border: none;
            }
            
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #374151;
                color: #ffffff;
            }
            
            QTableWidget::item:selected {
                background-color: #334155;
            }
            
            QHeaderView::section {
                background-color: transparent;
                color: #9ca3af;
                padding: 10px;
                border: none;
                border-bottom: 1px solid #374151;
                font-weight: 600;
                font-size: 12px;
                text-align: left;
            }
        """)

        # Örnek veri (HTML tasarımından)
        example_data = [
            ["AKBNK", "200", "16.90 TL", "3,380 TL", "+450 TL"],
            ["THYAO", "400", "13.95 TL", "5,580 TL", "+800 TL"],
            ["SISE", "20", "4.675 TL", "93.50 TL", "+20 TL"],
            ["EREGL", "100", "7.995 TL", "799.50 TL", "-50 TL"],
        ]

        self.portfolio_table.setRowCount(len(example_data))
        for row, data in enumerate(example_data):
            for col, value in enumerate(data):
                item = QTableWidgetItem(value)
                item_font = QFont('Arial', 12)
                item.setFont(item_font)
                
                # Kar/Zarar rengini ayarla
                if col == 4:
                    if "-" in value:
                        item.setForeground(QBrush(QColor("#ef4444")))
                    else:
                        item.setForeground(QBrush(QColor("#22c55e")))
                else:
                    item.setForeground(QBrush(QColor("#ffffff")))
                
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.portfolio_table.setItem(row, col, item)

        layout.addWidget(self.portfolio_table)
        widget.setLayout(layout)
        return widget

    def _create_quick_trade_panel(self) -> QWidget:
        """Sağ taraf: Hızlı İşlem paneli (HTML tasarımı)."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #1e293b;
                border: none;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        # Başlık
        title_label = QLabel("Hızlı İşlem")
        title_font = QFont('Arial', 13, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        layout.addWidget(title_label)

        layout.addSpacing(15)

        # Hisse Kodu
        self.quick_hisse = QLineEdit()
        self.quick_hisse.setPlaceholderText("Hisse Kodu")
        self.quick_hisse.setFixedHeight(40)
        layout.addWidget(self.quick_hisse)

        # Adet
        self.quick_quantity = QLineEdit()
        self.quick_quantity.setPlaceholderText("Adet")
        self.quick_quantity.setFixedHeight(40)
        layout.addWidget(self.quick_quantity)

        # Fiyat
        self.quick_price = QLineEdit()
        self.quick_price.setPlaceholderText("Fiyat")
        self.quick_price.setFixedHeight(40)
        layout.addWidget(self.quick_price)

        layout.addSpacing(10)

        # İşlem Yap butonu
        trade_btn = QPushButton("İşlem Yap")
        trade_btn.setFixedHeight(45)
        trade_btn.setObjectName("primaryBtn")
        trade_btn.setStyleSheet("""
            QPushButton#primaryBtn {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton#primaryBtn:hover {
                background-color: #2563eb;
            }
            QPushButton#primaryBtn:pressed {
                background-color: #1d4ed8;
            }
        """)
        trade_btn.clicked.connect(self._handle_quick_trade)
        layout.addWidget(trade_btn)

        layout.addStretch()
        panel.setLayout(layout)
        return panel

    def load_data(self):
        """Verileri yükle."""
        try:
            self.portfolio_summary = self.api_client.get_portfolio_summary()
            transactions_response = self.api_client.get_transactions()
            self.transactions = [
                Transaction.from_dict(t) for t in transactions_response.get('transactions', [])
            ]
        except APIError as e:
            QMessageBox.critical(self, "Hata", f"Veri yükleme hatası: {str(e)}")

    def _handle_quick_trade(self):
        """Hızlı işlem ekle."""
        try:
            if not self.quick_hisse.text() or not self.quick_quantity.text() or not self.quick_price.text():
                QMessageBox.warning(self, "Uyarı", "Lütfen tüm alanları doldurunuz!")
                return

            data = {
                "stock_symbol": self.quick_hisse.text().upper(),
                "stock_name": self.quick_hisse.text().upper(),
                "transaction_type": "BUY",
                "quantity": float(self.quick_quantity.text()),
                "price_per_unit": float(self.quick_price.text()),
                "commission": 0.0,
                "transaction_date": QDateTime.currentDateTime().toPyDateTime().isoformat(),
            }

            self.api_client.create_transaction(data)
            QMessageBox.information(self, "Başarı", "İşlem başarıyla eklendi!")
            self.quick_hisse.clear()
            self.quick_quantity.clear()
            self.quick_price.clear()
            self.load_data()

        except ValueError:
            QMessageBox.critical(self, "Hata", "Adet ve Fiyat sayısal değer olmalıdır!")
        except APIError as e:
            QMessageBox.critical(self, "Hata", f"İşlem ekleme hatası: {str(e)}")

    def _handle_delete_transaction(self, transaction_id: int):
        """İşlem silme."""
        reply = QMessageBox.question(
            self, "Onay",
            "Bu işlemi silmek istediğinize emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.api_client.delete_transaction(transaction_id)
                QMessageBox.information(self, "Başarı", "İşlem silindi!")
                self.load_data()
            except APIError as e:
                QMessageBox.critical(self, "Hata", f"Silme hatası: {str(e)}")

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
