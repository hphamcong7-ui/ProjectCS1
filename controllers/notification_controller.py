"""NotificationController - quản lý thông báo cho người dùng và admin."""

from datetime import datetime
import sqlite3

from controllers.database_connection import DatabaseConnection
from models.notification import Notification


class NotificationController:
    """Xử lý lưu trữ và đọc thông báo ứng dụng."""

    def __init__(self):
        self.db = DatabaseConnection()

    def create_notification(self, title, message, user_id=None, type_='info'):
        """Tạo thông báo mới và lưu vào cơ sở dữ liệu."""
        query = """
            INSERT INTO notifications (user_id, title, message, created_at, is_read, type)
            VALUES (?, ?, ?, ?, 0, ?)
        """
        # Sử dụng ISO format chuẩn để lưu trữ thời gian đồng bộ
        current_time = datetime.utcnow().isoformat()
        
        params = (
            user_id,
            title,
            message,
            current_time,
            type_,
        )
        try:
            self.db.execute_non_query(query, params)
        except Exception as e:
            print(f"Lỗi khi tạo thông báo hệ thống: {e}")

    def get_notifications(self, user_id=None, unread_only=False, is_admin_view=False):
        """
        Lấy danh sách thông báo được ánh xạ sang thực thể Model đối tượng.
        - user_id: ID của người dùng cần lọc.
        - unread_only: Chỉ lấy các thông báo chưa đọc.
        - is_admin_view: Nếu True và user_id là Admin, cho phép thấy các thông báo hệ thống (user_id IS NULL).
        """
        query = """
            SELECT notification_id, user_id, title, message, created_at, is_read, type
            FROM notifications
        """
        params = []
        conditions = []

        # Xử lý phân quyền lọc dữ liệu thông báo nghiêm ngặt
        if user_id is not None:
            if is_admin_view:
                # Admin được xem thông báo của chính mình VÀ các thông báo toàn hệ thống (user_id là NULL)
                conditions.append("(user_id = ? OR user_id IS NULL)")
                params.append(user_id)
            else:
                # User thường chỉ được xem thông báo đích danh của chính mình
                conditions.append("user_id = ?")
                params.append(user_id)
        elif not is_admin_view:
            # Nếu không truyền user_id và không phải quyền xem của Admin, cô lập dữ liệu
            conditions.append("user_id IS NULL")

        if unread_only:
            conditions.append("is_read = 0")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY created_at DESC"

        try:
            results = self.db.execute_query(query, tuple(params) if params else None)
            notifications = []
            if results:
                for row in results:
                    notifications.append(
                        Notification(
                            notification_id=row['notification_id'],
                            user_id=row['user_id'],
                            title=row['title'],
                            message=row['message'],
                            created_at=row['created_at'],
                            is_read=row['is_read'],
                            type_=row['type'],
                        )
                    )
            return notifications
        except Exception as e:
            print(f"Lỗi khi tải danh sách thông báo: {e}")
            return []

    def mark_as_read(self, notification_id):
        """Đánh dấu thông báo cụ thể là đã đọc."""
        query = "UPDATE notifications SET is_read = 1 WHERE notification_id = ?"
        try:
            # Ép kiểu tường minh thành tuple để tránh lỗi nhận diện sai cú pháp đơn tử trên SQLite
            self.db.execute_non_query(query, tuple([notification_id]))
            return True
        except Exception as e:
            print(f"Lỗi khi cập nhật trạng thái đã đọc của thông báo #{notification_id}: {e}")
            return False

    def mark_all_as_read(self, user_id=None):
        """Đánh dấu tất cả thông báo của một người dùng là đã đọc."""
        query = "UPDATE notifications SET is_read = 1 WHERE is_read = 0"
        params = []
        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        try:
            self.db.execute_non_query(query, tuple(params) if params else None)
            return True
        except Exception as e:
            print(f"Lỗi khi đánh dấu đọc toàn bộ thông báo: {e}")
            return False

    def get_unread_count(self, user_id=None, is_admin_view=False):
        """Lấy số lượng thông báo chưa đọc phục vụ hiển thị Badge số lượng trên UI."""
        query = "SELECT COUNT(*) AS cnt FROM notifications WHERE is_read = 0"
        params = []
        
        if user_id is not None:
            if is_admin_view:
                query += " AND (user_id = ? OR user_id IS NULL)"
                params.append(user_id)
            else:
                query += " AND user_id = ?"
                params.append(user_id)
        else:
            query += " AND user_id IS NULL"

        try:
            results = self.db.execute_query(query, tuple(params) if params else None)
            return results[0]['cnt'] if results else 0
        except Exception as e:
            print(f"Lỗi khi tính toán số lượng thông báo chưa đọc: {e}")
            return 0