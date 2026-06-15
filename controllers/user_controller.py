"""Controller xử lý các thao tác với người dùng - Phiên bản Plain-text."""

from datetime import datetime
from controllers.database_connection import DatabaseConnection
from models.user import User


class UserController:
    """Xử lý nghiệp vụ người dùng không sử dụng mã hóa mật khẩu."""

    def __init__(self):
        self.db = DatabaseConnection()

    def login(self, identifier, password):
        """
        Xác thực đăng nhập an toàn bằng cơ chế tương thích mọi định dạng dữ liệu.
        Hỗ trợ đối chiếu chuỗi thô và chuỗi mã hóa SHA-256 tự động.
        """
        if not identifier or not password:
            return None

        identifier = str(identifier).strip().lower()
        password = str(password).strip()

        try:
            # Truy vấn toàn bộ bảng để kiểm tra thủ công, tránh lỗi liên kết tham số bound parameters
            results = self.db.execute_query("SELECT * FROM users")
            if not results:
                return None

            for row in results:
                # Sử dụng cơ chế bọc lỗi để tự động nhận diện cấu trúc dữ liệu trả về từ DB
                try:
                    # Trường hợp dữ liệu trả về dạng Dictionary hoặc sqlite3.Row
                    u_id = str(row['user_id']).lower()
                    u_name = str(row['full_name'])
                    u_email = str(row['email']).lower()
                    u_pw = str(row['password_hash'])
                    u_role = str(row['role'])
                except (TypeError, KeyError, IndexError):
                    # Trường hợp dữ liệu trả về dạng Tuple nguyên bản theo thứ tự cột
                    u_id = str(row[0]).lower()
                    u_name = str(row[1])
                    u_email = str(row[2]).lower()
                    u_pw = str(row[4])
                    u_role = str(row[5])

                # Kiểm tra trùng khớp tài khoản (chấp nhận cả mã định danh hoặc email)
                if u_id == identifier or u_email == identifier:
                    # Tạo chuỗi mã hóa dự phòng trường hợp cơ sở dữ liệu đã băm mật khẩu trước đó
                    import hashlib
                    hashed_input = hashlib.sha256(password.encode()).hexdigest()

                    # Đối chiếu: Hợp lệ nếu khớp mật khẩu thô HOẶC khớp chuỗi băm SHA-256
                    if u_pw == password or u_pw == hashed_input:
                        return User(
                            user_id=u_id,
                            full_name=u_name,
                            email=u_email,
                            role=u_role
                        )
        except Exception as e:
            print(f"Lỗi hệ thống trong quá trình xác thực dữ liệu: {e}")
        
        return None

    def _row_to_user(self, row):
        return User(
            user_id=row['user_id'],
            full_name=row['full_name'],
            email=row['email'],
            role=row['role']
        )

    def get_all_users(self):
        query = "SELECT * FROM users WHERE is_active = 1"
        results = self.db.execute_query(query)
        return [self._row_to_user(row) for row in (results or [])]

    def get_user_by_id(self, user_id):
        query = "SELECT * FROM users WHERE user_id = ? AND is_active = 1"
        results = self.db.execute_query(query, (user_id,))
        return self._row_to_user(results[0]) if results else None

    def create_user(self, user: User, password):
        if not password:
            raise Exception("Mật khẩu không được để trống.")
        current_time = datetime.utcnow().isoformat()
        
        query = """
            INSERT INTO users (user_id, full_name, email, role, password_hash, created_at, is_active)
            VALUES (?, ?, ?, ?, ?, ?, 1)
        """
        self.db.execute_non_query(query, (user.user_id, user.full_name, user.email, user.role, password, current_time))

    def update_user(self, user: User, password=None):
        if password:
            query = """
                UPDATE users SET full_name = ?, email = ?, role = ?, password_hash = ? WHERE user_id = ?
            """
            params = (user.full_name, user.email, user.role, password, user.user_id)
        else:
            query = """
                UPDATE users SET full_name = ?, email = ?, role = ? WHERE user_id = ?
            """
            params = (user.full_name, user.email, user.role, user.user_id)
        self.db.execute_non_query(query, params)

    def delete_user(self, user_id):
        query = "UPDATE users SET is_active = 0 WHERE user_id = ?"
        self.db.execute_non_query(query, (user_id,))

    def search_users(self, keyword):
        like_keyword = f"%{keyword}%"
        query = """
            SELECT * FROM users WHERE is_active = 1 AND (user_id LIKE ? OR full_name LIKE ? OR email LIKE ?)
        """
        results = self.db.execute_query(query, (like_keyword, like_keyword, like_keyword))
        return [self._row_to_user(row) for row in (results or [])]