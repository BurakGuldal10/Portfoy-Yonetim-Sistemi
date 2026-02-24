"""
Logging Konfigürasyonu
========================
Uygulamada tüm event'ler bu logger üzerinden kaydedilir.
"""

import logging
import sys
from pathlib import Path

# Log dosyası dizinini oluştur
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Logger oluştur
logger = logging.getLogger("finans_takip")
logger.setLevel(logging.DEBUG)

# Format: [ZAMAN] [LEVEL] [MODULE] - MESAJ
formatter = logging.Formatter(
    fmt='[%(asctime)s] [%(levelname)-8s] [%(name)s] - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Console Handler (stdout) - UTF-8 encoding for emoji support
try:
    # Windows compatibility: Use UTF-8 for console
    import io
    if sys.platform == 'win32':
        console_handler = logging.StreamHandler(io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8'))
    else:
        console_handler = logging.StreamHandler(sys.stdout)
except:
    console_handler = logging.StreamHandler(sys.stdout)

console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# File Handler (logs/app.log)
file_handler = logging.FileHandler(logs_dir / "app.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Hata logları için ayrı dosya (logs/errors.log)
error_handler = logging.FileHandler(logs_dir / "errors.log", encoding="utf-8")
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)
logger.addHandler(error_handler)


def get_logger(name: str) -> logging.Logger:
    """İçinden çağrılan modül için logger alır."""
    return logging.getLogger(f"finans_takip.{name}")
