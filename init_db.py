"""Khởi tạo cơ sở dữ liệu sử dụng mật khẩu thô không mã hóa."""

import sqlite3
from datetime import datetime
from config.database_config import get_database_path

def init_database():
    db_path = get_database_path()
    print(f"Đang đồng bộ và khởi tạo cơ sở dữ liệu thô tại: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Khởi tạo cấu trúc bảng users
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            password_hash TEXT NOT NULL, -- Vẫn giữ tên cột cũ để tránh sửa đổi Model
            role TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            device_name TEXT NOT NULL,
            category TEXT NOT NULL,
            total_quantity INTEGER NOT NULL DEFAULT 0,
            available_quantity INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Có sẵn'
        )
    """)

    # Sử dụng mật khẩu văn bản thô trực tiếp
    plain_password = "123456"
    current_time = datetime.utcnow().isoformat()

    # Nạp dữ liệu tài khoản chuẩn
    users_data = [
        ('admin', 'Quản trị viên Hệ thống', 'admin@lab.local', '0123456789', plain_password, 'Admin', current_time, 1),
        ('user01', 'Người mượn Thiết bị', 'user@lab.local', '0987654321', plain_password, 'User', current_time, 1)
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO users 
        (user_id, full_name, email, phone, password_hash, role, created_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, users_data)

    conn.commit()
    conn.close()
    
    print("\n--- HOÀN TẤT THIẾT LẬP MẬT KHẨU THÔ ---")
    print("Mã đăng nhập: admin | Mật khẩu: 123456")

if __name__ == "__main__":
    init_database()