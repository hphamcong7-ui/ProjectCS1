"""
Điểm khởi chạy ứng dụng
"""

import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from views.login_view import LoginDialog
from views.main_window import MainWindow
from controllers.database_connection import DatabaseConnection

def main():
    """Hàm main - khởi chạy ứng dụng"""
    
    # Tạo ứng dụng Qt
    app = QApplication(sys.argv)
    app.setStyle('Fusion') 
    
    # Kiểm tra kết nối database trước khi khởi động
    try:
        db = DatabaseConnection()
        db.get_connection()
        print("Kết nối database thành công!")
    except Exception as e:
        QMessageBox.critical(
            None,
            "Lỗi kết nối Database",
            f"Không thể kết nối đến SQLite!\n\n"
            f"Chi tiết lỗi: {str(e)}\n\n"
            f"Vui lòng kiểm tra:\n"
            f"1. File cơ sở dữ liệu SQLite tồn tại hoặc có thể tạo được\n"
            f"2. Cấu hình trong config/database_config.py\n"
            f"3. Quyền ghi vào thư mục data"
        )
        sys.exit(1)

    login_dialog = LoginDialog()
    if login_dialog.exec_() != login_dialog.Accepted:
        sys.exit(0)

    authenticated_user = login_dialog.authenticated_user
    window = MainWindow(authenticated_user)
    window.show()
    
    # Chạy vòng lặp sự kiện
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
