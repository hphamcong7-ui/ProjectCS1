"""Login dialog cho phép người dùng đăng nhập trước khi truy cập hệ thống."""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QHBoxLayout, QWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from controllers.user_controller import UserController
from views.theme import get_button_style, get_stylesheet


class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_controller = UserController()
        self.authenticated_user = None
        
        self.setWindowTitle("Đăng nhập hệ thống")
        self.setFixedSize(420, 320)
        self.setStyleSheet(get_stylesheet(is_dark=False))
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 35, 35, 35)
        main_layout.setSpacing(15)

        title = QLabel("ĐĂNG NHẬP")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #0f172a;")
        main_layout.addWidget(title)

        description = QLabel("Hệ thống Quản lý Thiết bị Phòng Thí nghiệm")
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #64748b; font-size: 12px;")
        main_layout.addWidget(description)

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(12)
        
        self.txt_username = QLineEdit()
        self.txt_username.setPlaceholderText("Nhập Email hoặc Mã định danh (ID)")
        self.txt_username.setMinimumHeight(35)
        form_layout.addRow("Tài khoản:", self.txt_username)

        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Nhập mật khẩu")
        self.txt_password.setMinimumHeight(35)
        form_layout.addRow("Mật khẩu:", self.txt_password)

        main_layout.addWidget(form_widget)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        self.btn_login = QPushButton("Đăng nhập")
        self.btn_login.setMinimumHeight(38)
        self.btn_login.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_login.clicked.connect(self.login)
        self.btn_login.setDefault(True)
        btn_layout.addWidget(self.btn_login)

        self.btn_cancel = QPushButton("Thoát")
        self.btn_cancel.setMinimumHeight(38)
        self.btn_cancel.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_cancel)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

    def login(self):
        username = self.txt_username.text().strip()
        password = self.txt_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng nhập đầy đủ thông tin tài khoản.")
            return

        try:
            user = self.user_controller.login(username, password)
            if user:
                if hasattr(user, 'role'):
                    user.role = str(user.role).lower()
                else:
                    user.role = 'user'
                    
                self.authenticated_user = user
                self.accept()
            else:
                QMessageBox.critical(self, "Lỗi đăng nhập", "Thông tin tài khoản hoặc mật khẩu không chính xác.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", f"Lỗi xử lý phiên đăng nhập: {str(e)}")