import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "lab_management.db"


def get_database_path():
    """Trả về đường dẫn file SQLite và đảm bảo thư mục dữ liệu tồn tại."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return str(DATABASE_PATH)
