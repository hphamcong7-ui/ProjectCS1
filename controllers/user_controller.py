import hashlib
from datetime import datetime
from controllers.database_connection import DatabaseConnection
from models.user import User


class UserController:
    def __init__(self):
        self.db = DatabaseConnection()

    def login(self, identifier, password):
        if not identifier or not password:
            return None

        identifier = str(identifier).strip().lower()
        password = str(password).strip()
        hashed_pw = hashlib.sha256(password.encode()).hexdigest()

        try:
            # Check cả email và user_id. Giao DB lọc data để tránh tràn RAM
            query = "SELECT * FROM users WHERE (lower(user_id) = ? OR lower(email) = ?) AND is_active = 1"
            results = self.db.execute_query(query, (identifier, identifier))

            if not results:
                return None

            row = results[0]
            db_pw = str(row['password_hash'])

            # Support login bằng cả plaintext legacy hoặc sha256
            if db_pw in (password, hashed_pw):
                return self._row_to_user(row)
                
        except Exception as e:
            print(f"Login validation error: {e}")
            
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