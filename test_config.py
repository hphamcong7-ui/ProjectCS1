import os
from pathlib import Path
# Giả lập đường dẫn như trong app
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "lab_management.db"

print(f"--- ĐƯỜNG DẪN ỨNG DỤNG ĐANG TÌM: ---")
print(f"{DATABASE_PATH}")
print(f"--- KIỂM TRA TỒN TẠI ---")
print(f"File có tồn tại không? {os.path.exists(DATABASE_PATH)}")

if os.path.exists(DATABASE_PATH):
    import sqlite3
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id, email, password_hash FROM users")
        data = cursor.fetchall()
        print(f"Dữ liệu tìm thấy: {data}")
    except Exception as e:
        print(f"Lỗi đọc DB: {e}")
    conn.close()