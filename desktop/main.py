#!/usr/bin/env python3
"""
Portföy Yönetim Sistemi - Masaüstü Uygulaması
===============================================

Çalıştırma:
    python main.py
"""

import sys
import os

# QApplication'ı ÖNCE oluştur
from PyQt6.QtWidgets import QApplication
app_qt = QApplication(sys.argv)

# Matplotlib backend'ini ayarla (lazy import)
def setup_matplotlib():
    import matplotlib
    matplotlib.use('qtagg')

# Proje root'unu sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import Application


if __name__ == '__main__':
    try:
        setup_matplotlib()
        app = Application(app_qt)
        sys.exit(app.run())
    except KeyboardInterrupt:
        print(" Uygulamadan kapatıldı")
        sys.exit(0)
    except Exception as e:
        print(f"Hata: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
        import traceback
        traceback.print_exc()
        sys.exit(1)
