"""
Transaction History Page - İşlem Geçmişi Sayfası
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox,
    QScrollArea, QFrame, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QBrush

from src.api.client import APIClient, APIError
from src.models.data_models import Transaction


class TransactionHistoryPage(QWidget):
    """İşlem Geçmişi sayfası widget'ı."""

    def __init__(self, api_client: APIClient):
        """
        Args:
            api_client: API istemcisi
        """
        super().__init__()
        self.api_client = api_client
        self.init_ui()
        # refresh_data() çağrısını kaldırdık - ilk yükleme yapmıyor
        # self.refresh_data()

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
        scroll_layout.setContentsMargins(24, 24, 24, 24)
        scroll_layout.setSpacing(20)

        # Başlık
        title_label = QLabel("İşlem Geçmişi")
        title_font = QFont('Segoe UI', 20, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #ffffff; margin-bottom: 8px;")
        scroll_layout.addWidget(title_label)

        # Filtreler ve arama
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(12)

        # Hisse filtresi
        stock_filter_label = QLabel("Hisse:")
        stock_filter_label.setStyleSheet("color: #94a3b8; font-size: 12px;")
        filter_layout.addWidget(stock_filter_label)

        self.stock_filter = QComboBox()
        self.stock_filter.addItem("Tümü", None)
        self.stock_filter.setFixedHeight(36)
        self.stock_filter.currentIndexChanged.connect(self.refresh_data)
        filter_layout.addWidget(self.stock_filter)

        filter_layout.addStretch()

        # Yenile butonu
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setFixedHeight(36)
        refresh_btn.clicked.connect(self.refresh_data)
        filter_layout.addWidget(refresh_btn)

        scroll_layout.addLayout(filter_layout)

        # İşlem Geçmişi Tablosu
        history_table_frame = self._create_transaction_history_table()
        scroll_layout.addWidget(history_table_frame, 1)

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

    def _create_transaction_history_table(self) -> QFrame:
        """İşlem geçmişi tablosunu oluştur."""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(20, 28, 51, 0.7);
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 16px;
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
        header_layout.setContentsMargins(24, 24, 24, 24)

        title_label = QLabel("Tüm İşlemler")
        title_font = QFont('Segoe UI', 14, QFont.Weight.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        options_btn = QPushButton("⋮")
        options_btn.setFixedSize(32, 32)
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
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(8)
        self.history_table.setHorizontalHeaderLabels([
            "Tarih", "Hisse Kodu", "Hisse Adı", "Tip", "Adet",
            "Birim Fiyat", "Toplam", "Komisyon"
        ])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.history_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: transparent;
                border: none;
            }
        """)

        layout.addWidget(self.history_table)
        frame.setLayout(layout)
        return frame

    def refresh_data(self):
        """İşlem geçmişi tablosunu yenile."""
        try:
            # Filtre değerini al
            stock_filter = self.stock_filter.currentData()

            # API'den işlemleri çek
            transactions_response = self.api_client.get_transactions(
                page=1,
                page_size=100,
                stock_symbol=stock_filter
            )

            transactions = [
                Transaction.from_dict(t) for t in transactions_response.get('transactions', [])
            ]

            # Tabloyu doldur
            self.history_table.setRowCount(len(transactions))

            for row, transaction in enumerate(transactions):
                # Tarih
                date_str = transaction.transaction_date.strftime("%d.%m.%Y %H:%M")
                date_item = QTableWidgetItem(date_str)
                date_item.setFont(QFont('Segoe UI', 11))
                date_item.setForeground(QBrush(QColor("#94a3b8")))
                date_item.setFlags(date_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 0, date_item)

                # Hisse Kodu
                symbol_item = QTableWidgetItem(transaction.stock_symbol)
                symbol_item.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
                symbol_item.setForeground(QBrush(QColor("#22d3ee")))
                symbol_item.setFlags(symbol_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 1, symbol_item)

                # Hisse Adı
                name_item = QTableWidgetItem(transaction.stock_name or "-")
                name_item.setFont(QFont('Segoe UI', 11))
                name_item.setForeground(QBrush(QColor("#ffffff")))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 2, name_item)

                # Tip (BUY/SELL)
                type_text = "ALIŞ" if transaction.transaction_type == "BUY" else "SATIŞ"
                type_item = QTableWidgetItem(type_text)
                type_item.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
                if transaction.transaction_type == "BUY":
                    type_item.setForeground(QBrush(QColor("#10b981")))
                else:
                    type_item.setForeground(QBrush(QColor("#ef4444")))
                type_item.setFlags(type_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 3, type_item)

                # Adet
                qty_item = QTableWidgetItem(f"{transaction.quantity:.2f}")
                qty_item.setFont(QFont('Segoe UI', 11))
                qty_item.setForeground(QBrush(QColor("#ffffff")))
                qty_item.setFlags(qty_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 4, qty_item)

                # Birim Fiyat
                price_item = QTableWidgetItem(f"{transaction.price_per_unit:.2f} TL")
                price_item.setFont(QFont('Segoe UI', 11))
                price_item.setForeground(QBrush(QColor("#ffffff")))
                price_item.setFlags(price_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 5, price_item)

                # Toplam
                total_item = QTableWidgetItem(f"{transaction.total_amount:.2f} TL")
                total_item.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
                total_item.setForeground(QBrush(QColor("#ffffff")))
                total_item.setFlags(total_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 6, total_item)

                # Komisyon
                commission_item = QTableWidgetItem(f"{transaction.commission:.2f} TL")
                commission_item.setFont(QFont('Segoe UI', 11))
                commission_item.setForeground(QBrush(QColor("#94a3b8")))
                commission_item.setFlags(commission_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.history_table.setItem(row, 7, commission_item)

            # Hisse filtre listesini güncelle
            unique_stocks = sorted(set(t.stock_symbol for t in transactions))
            current_selection = self.stock_filter.currentData()
            self.stock_filter.clear()
            self.stock_filter.addItem("Tümü", None)
            for stock in unique_stocks:
                self.stock_filter.addItem(stock, stock)

            # Önceki seçimi geri yükle
            if current_selection:
                index = self.stock_filter.findData(current_selection)
                if index >= 0:
                    self.stock_filter.setCurrentIndex(index)

        except APIError as e:
            QMessageBox.critical(self, "Hata", f"İşlem geçmişi yüklenirken hata oluştu: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen hata: {str(e)}")

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
        layout.setContentsMargins(0, 16, 0, 16)

        # Sol taraf - Status
        status_label = QLabel("🟢 Tüm Sistemler Operasyonel")
        status_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;")
        layout.addWidget(status_label)

        layout.addStretch()

        # Sağ taraf - Info
        info_layout = QHBoxLayout()
        info_layout.setSpacing(24)

        build_label = QLabel("255 EIT 351")
        build_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold;")
        info_layout.addWidget(build_label)

        security_label = QLabel("🔒 PCI COMPLIANT")
        security_label.setStyleSheet("color: #94a3b8; font-size: 10px; font-weight: bold; text-transform: uppercase;")
        info_layout.addWidget(security_label)

        layout.addLayout(info_layout)

        footer.setLayout(layout)
        return footer
