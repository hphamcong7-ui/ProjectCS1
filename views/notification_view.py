"""NotificationView hiển thị danh sách thông báo và cho phép đánh dấu đã đọc."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox, QHBoxLayout,
    QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from controllers.notification_controller import NotificationController
from views.theme import get_button_style


class NotificationView(QWidget):
    """Giao diện Quản lý và theo dõi thông báo hệ thống."""

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.notification_controller = NotificationController()
        
        # Đồng bộ logic nhận diện phân quyền 
        self.user_role = str(self.current_user.role).lower() if (self.current_user and hasattr(self.current_user, 'role')) else 'user'
        
        self._init_ui()
        self.load_notifications()

    def _init_ui(self):
        self.layout = QVBoxLayout()
        # Áp dụng chuẩn Margin và Spacing rộng rãi (Minimalist)
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        header = QLabel("HỘP THƯ VÀ THÔNG BÁO")
        header.setFont(QFont("Segoe UI", 18, QFont.Bold))
        header.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.addWidget(header)

        # --- Bảng Dữ Liệu Thông Báo ---
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Người nhận', 'Tiêu đề', 'Nội dung', 'Thời gian', 'Trạng thái'
        ])
        
        # Tối ưu UI cho bảng theo chuẩn Flat Design
        self.table.verticalHeader().setVisible(False)
        self.table.verticalHeader().setDefaultSectionSize(45)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Phân bổ không gian cột: Nội dung và Tiêu đề được ưu tiên chiếm chỗ
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(2, QHeaderView.Stretch)
        header_view.setSectionResizeMode(3, QHeaderView.Stretch)
        header_view.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header_view.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        self.layout.addWidget(self.table)

        # --- Khu vực Nút chức năng ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)

        self.btn_mark_read = QPushButton("Đánh dấu đã đọc")
        self.btn_mark_read.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_mark_read.clicked.connect(self.mark_selected_read)
        action_layout.addWidget(self.btn_mark_read)

        self.btn_mark_all_read = QPushButton("Đọc tất cả")
        self.btn_mark_all_read.setStyleSheet(get_button_style("success", is_dark=False))
        self.btn_mark_all_read.clicked.connect(self.mark_all_read)
        action_layout.addWidget(self.btn_mark_all_read)

        action_layout.addStretch()

        self.btn_refresh = QPushButton("Làm mới hộp thư")
        self.btn_refresh.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_refresh.clicked.connect(self.load_notifications)
        action_layout.addWidget(self.btn_refresh)

        self.layout.addLayout(action_layout)
        self.setLayout(self.layout)

    def load_notifications(self):
        """Truy xuất và nạp dữ liệu thông báo vào bảng."""
        try:
            # Nếu là Admin, có thể xem được các thông báo toàn hệ thống (None)
            is_admin = (self.user_role == 'admin')
            
            # Hàm get_notifications đã được cập nhật logic an toàn ở Controller
            notifications = self.notification_controller.get_notifications(
                user_id=self.current_user.user_id if hasattr(self.current_user, 'user_id') else None,
                unread_only=False,
                is_admin_view=is_admin
            )

            self.table.setRowCount(0)
            if not notifications:
                return

            for note in notifications:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Xử lý format thời gian
                time_str = ''
                if note.created_at:
                    if isinstance(note.created_at, str):
                        # Cắt chuỗi ISO format để hiển thị gọn gàng (VD: 2026-06-15 14:30)
                        time_str = note.created_at[:16].replace('T', ' ')
                    else:
                        time_str = note.created_at.strftime('%d/%m/%Y %H:%M')

                # Ánh xạ dữ liệu
                target_user = str(note.user_id) if note.user_id else 'Toàn hệ thống'
                status_text = 'Đã đọc' if note.is_read else 'Chưa đọc'

                self.table.setItem(row, 0, QTableWidgetItem(str(note.notification_id)))
                self.table.setItem(row, 1, QTableWidgetItem(target_user))
                self.table.setItem(row, 2, QTableWidgetItem(str(note.title)))
                self.table.setItem(row, 3, QTableWidgetItem(str(note.message)))
                self.table.setItem(row, 4, QTableWidgetItem(time_str))
                
                # Highlight thông báo chưa đọc bằng màu chữ đậm/khác biệt
                status_item = QTableWidgetItem(status_text)
                if not note.is_read:
                    status_item.setForeground(Qt.red)
                    font = status_item.font()
                    font.setBold(True)
                    status_item.setFont(font)
                
                self.table.setItem(row, 5, status_item)
                
        except Exception as exc:
            QMessageBox.critical(self, 'Lỗi hệ thống', f"Không thể tải danh sách thông báo: {str(exc)}")

    def mark_selected_read(self):
        """Xử lý hành động đánh dấu một hoặc nhiều thông báo cụ thể là đã đọc."""
        selected_rows = set(item.row() for item in self.table.selectedItems())
        if not selected_rows:
            QMessageBox.warning(self, 'Cảnh báo thao tác', 'Vui lòng chọn ít nhất một thông báo trên bảng!')
            return
            
        try:
            success_count = 0
            for row in selected_rows:
                note_id_str = self.table.item(row, 0).text()
                if note_id_str.isdigit():
                    if self.notification_controller.mark_as_read(int(note_id_str)):
                        success_count += 1
                        
            if success_count > 0:
                self.load_notifications()
        except Exception as exc:
            QMessageBox.critical(self, 'Lỗi', f"Thao tác thất bại: {str(exc)}")

    def mark_all_read(self):
        """Đánh dấu toàn bộ thông báo thuộc quyền sở hữu là đã đọc."""
        try:
            user_id = getattr(self.current_user, 'user_id', getattr(self.current_user, 'id', None))
            # Nếu là Admin, có thể gọi cập nhật cho toàn hệ thống
            if self.user_role == 'admin':
                success = self.notification_controller.mark_all_as_read(user_id=None)
            else:
                success = self.notification_controller.mark_all_as_read(user_id=user_id)
                
            if success:
                self.load_notifications()
        except Exception as exc:
            QMessageBox.critical(self, 'Lỗi', f"Thao tác hàng loạt thất bại: {str(exc)}")