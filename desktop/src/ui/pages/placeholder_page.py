"""
Placeholder Page - Gelecekte eklenecek sayfalar için placeholder
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class PlaceholderPage(QWidget):
    """Placeholder sayfa widget'ı."""

    def __init__(self, message: str = "Bu sayfa yakında eklenecek"):
        """
        Args:
            message: Gösterilecek mesaj
        """
        super().__init__()
        self.message = message
        self.init_ui()

    def init_ui(self):
        """UI'yi başlat."""
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(self.message)
        label.setFont(QFont('Segoe UI', 16))
        label.setStyleSheet("color: #94a3b8;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)
