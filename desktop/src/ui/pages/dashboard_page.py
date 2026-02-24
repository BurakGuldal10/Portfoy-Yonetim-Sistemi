"""
Dashboard Page - Ana Dashboard Sayfası
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea, 
    QFrame, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtGui import QFont, QColor, QBrush

from src.api.client import APIClient, APIError
from src.models.data_models import Transaction


class DashboardPage(QWidget):
    """Dashboard sayfası widget'ı."""

    def __init__(self, api_client: APIClient, session):
        """
        Args:
            api_client: API istemcisi
            session: Oturum yöneticisi
        """
        super().__init__()
        self.api_client = api_client
        self.session = session
        self.init_ui()

    def init_ui(self):
        """UI'yi başlat."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                background-color: #0a0e1a;
                border: none;
            }
        """)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(16, 16, 16, 16)
        scroll_layout.setSpacing(12)

        # Summary Cards
        summary_cards = self._create_summary_cards()
        scroll_layout.addLayout(summary_cards)

        # Chart widget (full width)
        chart_widget = self._create_chart_widget()
        scroll_layout.addWidget(chart_widget, 1)

        # Portfolio Table
        portfolio_table = self._create_portfolio_table()
        scroll_layout.addWidget(portfolio_table)

        # Footer
        footer = self._create_footer()
        scroll_layout.addWidget(footer)

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)

        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def _create_summary_cards(self) -> QHBoxLayout:
        """Özet kartları oluştur (Daha kompakt)."""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)

        cards_data = [
            ("💰", "Toplam Portföy", "24,350 TL", "#3b82f6", False),
            ("📈", "Günlük Kar/Zarar", "+450 TL", "#10b981", True),
            ("📊", "Toplam Hisse", "7 Adet", "#eab308", False),
        ]

        for icon, title, value, color, is_positive in cards_data:
            card = self._create_glass_card(icon, title, value, color, is_positive)
            layout.addWidget(card)

        return layout

    def _create_glass_card(self, icon: str, title: str, value: str, color: str, is_positive: bool) -> QFrame:
        """Zarif, ince ve kompakt bir özet kartı."""
        card = QFrame()
        card.setMinimumWidth(220)
        card.setFixedHeight(75) # Daha kompakt yükseklik
        
        color_map = {
            "#3b82f6": "59, 130, 246",
            "#10b981": "16, 185, 129",
            "#eab308": "234, 179, 8"
        }
        rgb_color = color_map.get(color, "255, 255, 255")

        card.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(30, 41, 59, 0.4);
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 15px;
            }}
            QFrame:hover {{
                background-color: rgba(51, 65, 85, 0.5);
                border: 1px solid rgba({rgb_color}, 0.25);
            }}
        """)

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(12, 10, 12, 10)
        main_layout.setSpacing(12)

        # Narin Vurgu Çubuğu
        accent_bar = QFrame()
        accent_bar.setFixedWidth(2)
        accent_bar.setFixedHeight(28)
        accent_bar.setStyleSheet(f"background-color: {color}; border-radius: 1px;")
        main_layout.addWidget(accent_bar)

        # İkon Çerçevesi
        icon_frame = QFrame()
        icon_frame.setFixedSize(38, 38)
        icon_frame.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({rgb_color}, 0.08);
                border-radius: 10px;
                border: 1px solid rgba({rgb_color}, 0.15);
            }}
        """)
        icon_layout = QVBoxLayout()
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_label = QLabel(icon)
        icon_label.setFont(QFont('Segoe UI', 14))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_layout.addWidget(icon_label)
        icon_frame.setLayout(icon_layout)
        main_layout.addWidget(icon_frame)

        # İçerik
        content_layout = QVBoxLayout()
        content_layout.setSpacing(0)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 8, QFont.Weight.Normal))
        title_label.setStyleSheet("color: #94a3b8;")

        value_label = QLabel(value)
        value_label.setFont(QFont('Segoe UI', 13, QFont.Weight.Bold))
        if is_positive:
            value_label.setStyleSheet("color: #10b981;")
        else:
            value_label.setStyleSheet("color: #ffffff;")

        content_layout.addWidget(title_label)
        content_layout.addWidget(value_label)

        main_layout.addLayout(content_layout)
        main_layout.addStretch()

        card.setLayout(main_layout)
        return card

    def _create_chart_widget(self) -> QFrame:
        """Portföy grafiği - Daha kompakt."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 28, 51, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Başlık
        title_layout = QHBoxLayout()
        title_label = QLabel("Portföy Değer Değişimi")
        title_font = QFont('Segoe UI', 10, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff;")
        title_layout.addWidget(title_label)

        info_label = QLabel("↑ +6,420 TL")
        info_font = QFont('Segoe UI', 9, QFont.Weight.Bold)
        info_label.setFont(info_font)
        info_label.setStyleSheet("color: #10b981;")
        title_layout.addWidget(info_label)

        title_layout.addStretch()

        # Timeframe buttons
        timeframe_layout = QHBoxLayout()
        timeframe_layout.setSpacing(3)
        for period in ["1G", "1H", "1A", "1Y"]:
            btn = QPushButton(period)
            btn.setFixedSize(32, 22)
            if period == "1Y":
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 9px;
                        font-weight: 600;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.05);
                        color: #94a3b8;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                        border-radius: 4px;
                        font-size: 9px;
                        font-weight: 600;
                    }
                """)
            timeframe_layout.addWidget(btn)
        
        title_layout.addLayout(timeframe_layout)
        layout.addLayout(title_layout)

        # Grafik (matplotlib)
        try:
            from matplotlib.figure import Figure
            from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
            
            figure = Figure(figsize=(8, 2), dpi=100, facecolor='transparent', edgecolor='none')
            figure.subplots_adjust(left=0.04, right=0.96, top=0.90, bottom=0.15)

            ax = figure.add_subplot(111)
            ax.set_facecolor('transparent')

            # Sample data
            x = list(range(30))
            y = [20000 + i * 100 + (i % 3) * 200 for i in x]

            ax.plot(x, y, color='#22d3ee', linewidth=2, marker='o', markersize=3)
            ax.fill_between(x, y, alpha=0.1, color='#22d3ee')
            ax.grid(True, alpha=0.1, color='rgba(255,255,255,0.05)', linestyle='-', linewidth=0.5)

            # Styling
            ax.set_xlabel('')
            ax.set_ylabel('')
            for label in ax.get_xticklabels():
                label.set_color('#94a3b8')
                label.set_fontsize(8)
            for label in ax.get_yticklabels():
                label.set_color('#94a3b8')
                label.set_fontsize(8)

            ax.spines['left'].set_color('#1e293b')
            ax.spines['bottom'].set_color('#1e293b')
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)

            canvas = FigureCanvas(figure)
            layout.addWidget(canvas)
        except Exception as e:
            error_label = QLabel("Grafik yüklenemedi")
            error_label.setStyleSheet("color: #94a3b8;")
            layout.addWidget(error_label)

        frame.setLayout(layout)
        return frame

    def _create_portfolio_table(self) -> QFrame:
        """Portföy özeti tablosu (9 sütunlu)."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 28, 51, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 12px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(12, 8, 12, 8)

        title_label = QLabel("Portföy Özeti")
        title_font = QFont('Segoe UI', 9, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #94a3b8;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        # Yeni işlem ekle butonu
        add_btn = QPushButton("+")
        add_btn.setFixedSize(28, 28)
        add_btn.setObjectName("primaryBtn")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        add_btn.clicked.connect(self._handle_add_transaction)
        header_layout.addWidget(add_btn)

        options_btn = QPushButton("⋮")
        options_btn.setFixedSize(28, 28)
        options_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.05);
                color: #94a3b8;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout.addWidget(options_btn)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)

        # Tablo
        self.portfolio_table = QTableWidget()
        self.portfolio_table.setColumnCount(9)
        self.portfolio_table.setHorizontalHeaderLabels([
            "Hisse Kodu", "Hisse Adı", "Adet", "Ortalama Maliyet",
            "Güncel Fiyat", "Toplam Değer", "Kar/Zarar", "Alınış Tarihi", "Satış Tarihi"
        ])
        self.portfolio_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.portfolio_table.horizontalHeader().setDefaultSectionSize(40)
        self.portfolio_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.portfolio_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.portfolio_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
            }
            QTableWidget::item {
                background-color: transparent;
                padding: 4px;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item:selected {
                background-color: rgba(59, 130, 246, 0.1);
            }
            QHeaderView::section {
                background-color: transparent;
                color: #64748b;
                padding: 4px;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                font-size: 8px;
                font-weight: 600;
            }
        """)

        # Örnek veri
        data = [
            ["AKBNK", "Akbank T.A.Ş.", "200", "16.50 TL", "11.52 TL", "24,350 TL", "+6,400 TL", "12.01.2024", "-"],
            ["THYAO", "Türk Hava Yolları", "400", "13.95 TL", "15.34 TL", "6,136 TL", "+3,398 TL", "15.02.2024", "-"],
            ["SISE", "Şişe Cam", "20", "4.675 TL", "5.835 TL", "20,520 TL", "+6,998 TL", "03.03.2024", "-"],
            ["EREGL", "Erdemir", "100", "7.995 TL", "7.923 TL", "23,360 TL", "-920 TL", "28.02.2024", "-"],
        ]

        self.portfolio_table.setRowCount(len(data))
        self.portfolio_table.verticalHeader().setDefaultSectionSize(24)
        for row, row_data in enumerate(data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item_font = QFont('Segoe UI', 9)
                item.setFont(item_font)
                item.setBackground(QColor("transparent"))

                # Renklandırma
                if col == 0:  # Hisse Kodu
                    item.setForeground(QBrush(QColor("#22d3ee")))
                    item.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
                elif col == 6:  # Kar/Zarar
                    if "-" in value and value != "-":
                        item.setForeground(QBrush(QColor("#ef4444")))
                    else:
                        item.setForeground(QBrush(QColor("#10b981")))
                    item.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
                else:
                    item.setForeground(QBrush(QColor("#ffffff")))

                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.portfolio_table.setItem(row, col, item)

        layout.addWidget(self.portfolio_table)
        frame.setLayout(layout)
        return frame

    def _create_footer(self) -> QFrame:
        """Footer oluştur."""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border-top: 1px solid rgba(255, 255, 255, 0.05);
            }
        """)

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 12, 0, 12)

        # Sol taraf - Status
        status_label = QLabel("🟢 Tüm Sistemler Operasyonel")
        status_label.setStyleSheet("color: #94a3b8; font-size: 9px; font-weight: bold; text-transform: uppercase;")
        layout.addWidget(status_label)

        layout.addStretch()

        # Sağ taraf - Info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)

        build_label = QLabel("255 EIT 351")
        build_label.setStyleSheet("color: #94a3b8; font-size: 9px; font-weight: bold;")
        info_layout.addWidget(build_label)

        security_label = QLabel("🔒 PCI COMPLIANT")
        security_label.setStyleSheet("color: #94a3b8; font-size: 9px; font-weight: bold; text-transform: uppercase;")
        info_layout.addWidget(security_label)

        layout.addLayout(info_layout)

        footer.setLayout(layout)
        return footer

    def _handle_add_transaction(self):
        """Yeni işlem ekle butonu tıklandığında."""
        # Bu fonksiyon yeni işlem ekleme dialog'unu açacak
        # Şimdilik basit bir mesaj gösteriyoruz
        QMessageBox.information(
            self, 
            "Yeni İşlem", 
            "Yeni işlem ekleme özelliği yakında eklenecek.\n\nBu özellik sidebar'daki 'Yeni İşlem' menüsünden de erişilebilir olacak."
        )
