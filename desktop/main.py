#!/usr/bin/env python3
"""
Portföy Yönetim Sistemi - Masaüstü Uygulaması
===============================================

Çalıştırma:
    python main.py
"""

import sys
import os

# Proje root'unu sys.path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import main


if __name__ == '__main__':
    sys.exit(main())
