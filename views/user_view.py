"""Giao diện quản lý Người dùng."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView,
    QComboBox, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from controllers.user_controller import UserController
from models.user import User
from utils.validators import validate_user_input
from views.theme import get_button_style


class UserView(QWidget):
    """Widget quản lý người dùng với chức năng CRUD và phân quyền thiết kế phẳng."""

    def __init__(self):
        super().__init__()
        self.controller = UserController()
        self.selected_user_id = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        # Áp dụng chuẩn Margin và Spacing rộng rãi
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Tiêu đề phân hệ
        title_label = QLabel("QUẢN LÝ HỒ SƠ NGƯỜI DÙNG")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(title_label)

        # --- Khu vực Form nhập liệu ---
        input_group = QGroupBox("Thông tin chi tiết tài khoản")
        input_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)

        form_layout.addWidget(QLabel("Mã người dùng:"), 0, 0)
        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("VD: 25IC001")
        form_layout.addWidget(self.txt_id, 0, 1)

        form_layout.addWidget(QLabel("Họ và tên:"), 0, 2)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nhập đầy đủ họ tên")
        form_layout.addWidget(self.txt_name, 0, 3)

        form_layout.addWidget(QLabel("Email / Tài khoản:"), 1, 0)
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("email@domain.com")
        form_layout.addWidget(self.txt_email, 1, 1)

        form_layout.addWidget(QLabel("Phân quyền:"), 1, 2)
        self.cmb_role = QComboBox()
        # Chuẩn hóa giá trị role khớp với logic hệ thống (chữ thường khi xử lý, hiển thị hoa)
        self.cmb_role.addItems(["User", "Admin"])
        form_layout.addWidget(self.cmb_role, 1, 3)

        form_layout.addWidget(QLabel("Mật khẩu:"), 2, 0)
        self.txt_password = QLineEdit()
        self.txt_password.setEchoMode(QLineEdit.Password)
        self.txt_password.setPlaceholderText("Để trống nếu không đổi")
        form_layout.addWidget(self.txt_password, 2, 1)

        form_layout.addWidget(QLabel("Xác nhận MK:"), 2, 2)
        self.txt_confirm_password = QLineEdit()
        self.txt_confirm_password.setEchoMode(QLineEdit.Password)
        self.txt_confirm_password.setPlaceholderText("Nhập lại mật khẩu")
        form_layout.addWidget(self.txt_confirm_password, 2, 3)

        input_group.setLayout(form_layout)
        main_layout.addWidget(input_group)

        # --- Khu vực Nút bấm hành động và Tìm kiếm ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        self.btn_add = QPushButton("Thêm mới")
        self.btn_add.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_add.clicked.connect(self.add_user)
        
        self.btn_update = QPushButton("Cập nhật")
        self.btn_update.setStyleSheet(get_button_style("success", is_dark=False))
        self.btn_update.clicked.connect(self.update_user)
        
        self.btn_delete = QPushButton("Xóa")
        self.btn_delete.setStyleSheet(get_button_style("danger", is_dark=False))
        self.btn_delete.clicked.connect(self.delete_user)
        
        self.btn_clear = QPushButton("Làm mới form")
        self.btn_clear.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_clear.clicked.connect(self.clear_form)

        action_layout.addWidget(self.btn_add)
        action_layout.addWidget(self.btn_update)
        action_layout.addWidget(self.btn_delete)
        action_layout.addWidget(self.btn_clear)
        action_layout.addStretch()

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm theo mã, tên hoặc email...")
        self.txt_search.setMinimumWidth(300)
        self.txt_search.textChanged.connect(self.search_user)
        action_layout.addWidget(self.txt_search)

        main_layout.addLayout(action_layout)

        # --- Khu vực Bảng dữ liệu ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Mã hệ thống", "Họ và tên", "Email / Tài khoản", "Quyền hạn"
        ])
        
        # Tối ưu hóa UI cho TableWidget (Flat Design)
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.table.itemSelectionChanged.connect(self.on_select_row)
        main_layout.addWidget(self.table)

        # Phản hồi hệ thống trực tiếp (Inline Feedback)
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setAlignment(Qt.AlignCenter)
        self.lbl_feedback.setFont(QFont("Segoe UI", 10, QFont.Bold))
        main_layout.addWidget(self.lbl_feedback)

        self.setLayout(main_layout)

    def show_feedback(self, message, is_error=False):
        """Hiển thị phản hồi thao tác trực tiếp trên giao diện."""
        color = "#dc2626" if is_error else "#16a34a"
        self.lbl_feedback.setStyleSheet(f"color: {color}; padding: 5px;")
        self.lbl_feedback.setText(message)
        QTimer.singleShot(3000, lambda: self.lbl_feedback.setText(""))

    def load_data(self):
        try:
            users = self.controller.get_all_users()
            self._populate_table(users)
        except Exception as e:
            self.show_feedback(f"Lỗi tải dữ liệu người dùng: {str(e)}", is_error=True)

    def _populate_table(self, users):
        if users is None:
            return
        self.table.setRowCount(0)
        for user in users:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Xử lý truy xuất thuộc tính động an toàn
            u_id = getattr(user, 'user_id', getattr(user, 'id', ''))
            u_name = getattr(user, 'full_name', getattr(user, 'name', ''))
            u_email = getattr(user, 'email', '')
            u_role = getattr(user, 'role', '').capitalize()
            
            self.table.setItem(row, 0, QTableWidgetItem(str(u_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(u_name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(u_email)))
            self.table.setItem(row, 3, QTableWidgetItem(str(u_role)))

    def on_select_row(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        self.selected_user_id = self.table.item(row, 0).text()
        
        self.txt_id.setText(self.selected_user_id)
        self.txt_id.setReadOnly(True)
        self.txt_name.setText(self.table.item(row, 1).text())
        self.txt_email.setText(self.table.item(row, 2).text())
        
        # Thiết lập ComboBox phân quyền
        role_text = self.table.item(row, 3).text()
        index = self.cmb_role.findText(role_text, Qt.MatchFixedString)
        if index >= 0:
            self.cmb_role.setCurrentIndex(index)
            
        # Làm sạch ô mật khẩu để bảo mật và tránh hiểu nhầm
        self.txt_password.clear()
        self.txt_confirm_password.clear()

    def get_form_data(self):
        return {
            'user_id': self.txt_id.text().strip(),
            'full_name': self.txt_name.text().strip(),
            'email': self.txt_email.text().strip(),
            'role': self.cmb_role.currentText(),
            'password': self.txt_password.text() or None,
            'confirm_password': self.txt_confirm_password.text() or None
        }

    def clear_form(self):
        self.selected_user_id = None
        self.txt_id.clear()
        self.txt_id.setReadOnly(False)
        self.txt_name.clear()
        self.txt_email.clear()
        self.cmb_role.setCurrentIndex(0)
        self.txt_password.clear()
        self.txt_confirm_password.clear()
        self.table.clearSelection()

    def add_user(self):
        data = self.get_form_data()
        is_valid, msg = validate_user_input(**data)
        if not is_valid:
            self.show_feedback(msg, is_error=True)
            return
        try:
            user = User(
                user_id=data['user_id'],
                full_name=data['full_name'],
                email=data['email'],
                role=data['role'].lower() # Hạ cấp chuỗi để đồng bộ xử lý role trong DB
            )
            self.controller.create_user(user, data['password'])
            self.show_feedback("Ghi nhận người dùng mới thành công.")
            self.load_data()
            self.clear_form()
        except Exception as e:
            self.show_feedback(f"Từ chối tạo tài khoản: {str(e)}", is_error=True)

    def update_user(self):
        if not self.selected_user_id:
            self.show_feedback("Từ chối: Chưa chọn hồ sơ người dùng.", is_error=True)
            return

        data = self.get_form_data()
        
        # Bỏ qua validate mật khẩu nếu không có nhu cầu đổi
        if not data['password'] and not data['confirm_password']:
            data.pop('password', None)
            data.pop('confirm_password', None)
            is_valid, msg = validate_user_input(
                user_id=data['user_id'], full_name=data['full_name'], 
                email=data['email'], role=data['role']
            )
        else:
            is_valid, msg = validate_user_input(**data)

        if not is_valid:
            self.show_feedback(msg, is_error=True)
            return

        try:
            user = User(
                user_id=data['user_id'],
                full_name=data['full_name'],
                email=data['email'],
                role=data['role'].lower()
            )
            self.controller.update_user(user, data.get('password'))
            self.show_feedback("Cập nhật hồ sơ thành công.")
            self.load_data()
            self.clear_form()
        except Exception as e:
            self.show_feedback(f"Lỗi cập nhật: {str(e)}", is_error=True)

    def delete_user(self):
        if not self.selected_user_id:
            self.show_feedback("Vui lòng chọn người dùng cần xóa.", is_error=True)
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận xóa tài khoản",
            f"Tài khoản '{self.selected_user_id}' sẽ bị vô hiệu hóa. Tiếp tục?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_user(self.selected_user_id)
                self.show_feedback("✓ Đã xóa người dùng khỏi hệ thống.")
                self.load_data()
                self.clear_form()
            except Exception as e:
                self.show_feedback(f"Lỗi xóa dữ liệu: {str(e)}", is_error=True)

    def search_user(self):
        keyword = self.txt_search.text().strip()
        try:
            if keyword:
                users = self.controller.search_users(keyword)
            else:
                users = self.controller.get_all_users()
            self._populate_table(users)
        except Exception as e:
            self.show_feedback(f"Lỗi tìm kiếm: {str(e)}", is_error=True)