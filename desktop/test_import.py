#!/usr/bin/env python3
"""Test import sorununuu"""

import sys
import os

print("1. QApplication oluşturuluyor...")
from PyQt6.QtWidgets import QApplication
app_qt = QApplication(sys.argv)
print("2. QApplication başarıyla oluşturuldu!")

print("3. src.app import ediliyor...")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.app import Application
print("4. Application başarıyla import edildi!")

print("5. Application oluşturuluyor...")
app = Application(app_qt)
print("6. Application başarıyla oluşturuldu!")

print("7. app.run() çağrılıyor...")
sys.exit(app.run())
