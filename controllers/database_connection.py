import hashlib
import os
import sqlite3
from datetime import datetime

from config.database_config import get_database_path


class DatabaseConnection:
    """Singleton class quản lý kết nối SQLite và khởi tạo schema."""

    _instance = None
    _connection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self):
        """Trả về đối tượng kết nối SQLite và khởi tạo database khi cần."""
        if self._connection is None:
            database_path = get_database_path()
            db_dir = os.path.dirname(database_path)
            os.makedirs(db_dir, exist_ok=True)

            self._connection = sqlite3.connect(database_path, check_same_thread=False)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON;")
            self._initialize_database()

        return self._connection

    def _initialize_database(self):
        """Tạo các bảng và dữ liệu mặc định nếu chưa tồn tại."""
        connection = self._connection
        schema_script = """
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            phone TEXT,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS devices (
            device_id TEXT PRIMARY KEY,
            device_name TEXT NOT NULL,
            category TEXT NOT NULL,
            total_quantity INTEGER NOT NULL DEFAULT 0,
            available_quantity INTEGER NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'Có sẵn'
        );

        CREATE TABLE IF NOT EXISTS borrow_records (
            record_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            borrow_date TEXT NOT NULL,
            expected_return_date TEXT NOT NULL,
            actual_return_date TEXT,
            status TEXT NOT NULL,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS borrow_details (
            detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
            record_id TEXT NOT NULL,
            device_id TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            returned INTEGER NOT NULL DEFAULT 0,
            return_date TEXT,
            condition_on_return TEXT,
            FOREIGN KEY(record_id) REFERENCES borrow_records(record_id) ON DELETE CASCADE,
            FOREIGN KEY(device_id) REFERENCES devices(device_id) ON DELETE RESTRICT
        );

        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0,
            type TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE SET NULL
        );
        """

        cursor = connection.cursor()
        cursor.executescript(schema_script)
        connection.commit()

        self._create_default_admin(cursor)
        connection.commit()
        cursor.close()

    def _create_default_admin(self, cursor):
        """Tạo các tài khoản mặc định nếu cần."""
        admin_password = self._hash_password("123456")
        demo_user_password = self._hash_password("123456")

        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, full_name, email, phone, password_hash, role, created_at, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("admin", "Administrator", "admin@lab.local", "0123456789", admin_password, "Admin", datetime.utcnow().isoformat(), 1)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, full_name, email, phone, password_hash, role, created_at, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("borrower", "User Borrower", "borrower@lab.local", "0987654321", demo_user_password, "User", datetime.utcnow().isoformat(), 1)
        )
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, full_name, email, phone, password_hash, role, created_at, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("guest", "Tài khoản Demo", "guest@lab.local", "0909090909", demo_user_password, "User", datetime.utcnow().isoformat(), 1)
        )

    @staticmethod
    def _hash_password(password):
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def close_connection(self):
        if self._connection:
            try:
                self._connection.close()
            finally:
                self._connection = None

    def execute_query(self, query, params=None):
        """Thực thi câu truy vấn SELECT và trả về danh sách Row."""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return results
        except sqlite3.Error as e:
            raise Exception(f"Lỗi truy vấn dữ liệu: {str(e)}")

    def execute_non_query(self, query, params=None):
        """Thực thi INSERT/UPDATE/DELETE và trả về số dòng bị ảnh hưởng."""
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            connection.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            return rows_affected
        except sqlite3.Error as e:
            connection.rollback()
            raise Exception(f"Lỗi thực thi câu lệnh: {str(e)}")
    def create_tables(self):
     cursor = self.connection.cursor()
    
    # Bảng người dùng có phân quyền
     cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT,
                        role TEXT DEFAULT 'user' -- 'admin' hoặc 'user'
                    )''')
                    
    # Bảng thiết bị
     cursor.execute('''CREATE TABLE IF NOT EXISTS equipment (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        quantity INTEGER
                    )''')
                    
    # Bảng Hóa đơn gốc (Master) - Lưu thông tin thời gian và người mượn
     cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_record (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        borrow_date TEXT,
                        due_date TEXT,
                        status TEXT DEFAULT 'BORROWED',
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
                    
    # Bảng Chi tiết hóa đơn (Detail) - Lưu danh sách nhiều thiết bị
     cursor.execute('''CREATE TABLE IF NOT EXISTS borrow_detail (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        record_id INTEGER,
                        equipment_id INTEGER,
                        quantity INTEGER,
                        FOREIGN KEY(record_id) REFERENCES borrow_record(id),
                        FOREIGN KEY(equipment_id) REFERENCES equipment(id)
                    )''')
     self.connection.commit()