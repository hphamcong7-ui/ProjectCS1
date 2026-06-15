import sqlite3
import os
from config.database_config import get_database_path

def debug():
    db_path = get_database_path()
    print(f"--- ĐANG KIỂM TRA ĐƯỜNG DẪN: {db_path} ---")
    
    if not os.path.exists(db_path):
        print("LỖI: Không tìm thấy tệp cơ sở dữ liệu tại đường dẫn này!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        print(f"Tìm thấy {len(rows)} tài khoản trong bảng users:")
        for row in rows:
            # row: user_id, full_name, email, phone, password_hash, role, created_at, is_active
            print(f"- UserID: {row[0]}, Email: {row[2]}, Pass: {row[4]}, Role: {row[5]}")
    except Exception as e:
        print(f"LỖI KHI ĐỌC BẢNG: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug()