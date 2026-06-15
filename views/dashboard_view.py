"""Dashboard tổng quan hiển thị chỉ số và thống kê."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QTableWidget, QTableWidgetItem, QPushButton, QMessageBox,
    QHeaderView
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from controllers.borrow_controller import BorrowController
from controllers.report_controller import ReportController
from views.theme import get_button_style


class DashboardView(QWidget):
    """Giao diện Dashboard hiển thị số liệu thống kê với Flat Design."""

    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.borrow_controller = BorrowController()
        self.report_controller = ReportController()
        self._init_ui()
        self.load_data()

    def _init_ui(self):
        self.layout = QVBoxLayout()
        # Áp dụng khoảng không gian thoáng đãng
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.layout.setSpacing(20)

        title = QLabel("BẢNG ĐIỀU KHIỂN TỔNG QUAN")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.layout.addWidget(title)

        # --- Khu vực Thẻ thống kê (Metric Cards) ---
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        # Tạo thẻ với điểm nhấn màu sắc theo phong cách Modern UI
        self.card_total_devices = self._create_card("Tổng thiết bị trong kho", "0", "#3b82f6") # Blue
        self.card_borrowed = self._create_card("Thiết bị đang mượn", "0", "#f59e0b")      # Yellow
        self.card_available = self._create_card("Thiết bị khả dụng", "0", "#10b981")     # Green
        self.card_overdue = self._create_card("Đơn hàng quá hạn", "0", "#ef4444")        # Red
        
        summary_layout.addWidget(self.card_total_devices)
        summary_layout.addWidget(self.card_borrowed)
        summary_layout.addWidget(self.card_available)
        summary_layout.addWidget(self.card_overdue)
        
        self.layout.addLayout(summary_layout)

        # --- Khu vực Bảng thống kê chi tiết ---
        stats_label = QLabel("Thống kê nổi bật (Top 5)")
        stats_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        stats_label.setStyleSheet("color: #475569; margin-top: 10px;")
        self.layout.addWidget(stats_label)

        self.table_stats = QTableWidget(0, 3)
        self.table_stats.setHorizontalHeaderLabels(["Phân loại", "Chi tiết nhận diện", "Số lượng / Lượt"])
        self._setup_flat_table(self.table_stats)
        self.table_stats.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_stats.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.layout.addWidget(self.table_stats)

        # --- Khu vực Nút chức năng ---
        action_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("Trích xuất Lịch sử hệ thống (Excel/CSV)")
        self.btn_export.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_export.setMinimumHeight(35)
        self.btn_export.clicked.connect(self.export_history)
        
        self.btn_refresh = QPushButton("Làm mới dữ liệu")
        self.btn_refresh.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_refresh.setMinimumHeight(35)
        self.btn_refresh.clicked.connect(self.load_data)

        action_layout.addWidget(self.btn_export)
        action_layout.addStretch()
        action_layout.addWidget(self.btn_refresh)
        
        self.layout.addLayout(action_layout)
        self.setLayout(self.layout)

    def _setup_flat_table(self, table: QTableWidget):
        """Hàm tiện ích tối ưu giao diện bảng."""
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(45)
        table.setFocusPolicy(Qt.NoFocus)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

    def _create_card(self, title_text, value_text, color_hex):
        """Tạo thẻ hiển thị chỉ số với đường viền nổi bật bên trái."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: transparent;
                border: 1px solid #cbd5e1;
                border-radius: 8px;
                border-left: 5px solid {color_hex};
            }}
        """)
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel(title_text)
        title.setStyleSheet("color: #64748b; font-weight: bold; font-size: 13px; border: none;")
        
        # Gán thuộc tính động để lưu trữ label giá trị cập nhật sau này
        card.lbl_value = QLabel(value_text)
        card.lbl_value.setStyleSheet(f"color: {color_hex}; font-size: 26px; font-weight: bold; border: none;")
        
        layout.addWidget(title)
        layout.addWidget(card.lbl_value)
        card.setLayout(layout)
        return card

    def load_data(self):
        try:
            metrics = self.borrow_controller.get_dashboard_metrics()
            
            # Cập nhật số liệu trên các thẻ Card
            self.card_total_devices.lbl_value.setText(str(metrics.get('total_devices', 0)))
            self.card_borrowed.lbl_value.setText(str(metrics.get('borrowed_items', 0)))
            self.card_available.lbl_value.setText(str(metrics.get('available_items', 0)))
            self.card_overdue.lbl_value.setText(str(metrics.get('overdue_records', 0)))

            # Nạp dữ liệu thống kê vào bảng (Đã sửa lỗi đồng bộ truy xuất Dictionary)
            stats = self.borrow_controller.get_statistics()
            self.table_stats.setRowCount(0)
            
            if stats.get('most_borrowed'):
                for item in stats['most_borrowed']:
                    row = self.table_stats.rowCount()
                    self.table_stats.insertRow(row)
                    self.table_stats.setItem(row, 0, QTableWidgetItem('Thiết bị được mượn nhiều'))
                    self.table_stats.setItem(row, 1, QTableWidgetItem(f"[{item.get('device_id', '')}] {item.get('device_name', '')}"))
                    self.table_stats.setItem(row, 2, QTableWidgetItem(str(item.get('total_borrowed', 0))))
                    
            if stats.get('top_users'):
                for user in stats['top_users']:
                    row = self.table_stats.rowCount()
                    self.table_stats.insertRow(row)
                    self.table_stats.setItem(row, 0, QTableWidgetItem('User mượn nhiều nhất'))
                    self.table_stats.setItem(row, 1, QTableWidgetItem(f"[{user.get('user_id', '')}] {user.get('full_name', '')}"))
                    self.table_stats.setItem(row, 2, QTableWidgetItem(str(user.get('borrow_count', 0))))
                    
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi nạp dữ liệu", f"Hệ thống không thể tải dữ liệu Dashboard:\n{str(exc)}")

    def export_history(self):
        try:
            history = self.borrow_controller.get_borrow_history()
            headers = [
                'Mã đơn', 'Người mượn', 'Thiết bị', 'Số lượng',
                'Ngày mượn', 'Ngày trả DK', 'Ngày trả thực tế', 'Trạng thái'
            ]
            
            # Chuyển đổi dữ liệu Dictionary từ Database thành List 2 chiều để xuất Excel
            rows = []
            for record in history:
                rows.append([
                    record.get('record_id', ''),
                    record.get('full_name', ''),
                    record.get('device_name', ''),
                    record.get('quantity', ''),
                    record.get('borrow_date', '')[:10] if record.get('borrow_date') else '',
                    record.get('expected_return_date', '')[:10] if record.get('expected_return_date') else '',
                    record.get('actual_return_date', '')[:10] if record.get('actual_return_date') else 'Chưa trả',
                    record.get('status', '')
                ])
                
            filename = self.report_controller.create_report_filename('History_Export')
            
            import os
            # Đẩy file vào thư mục reports tập trung
            filepath = os.path.join(self.report_controller.export_dir, filename)
            
            result_msg = self.report_controller.export_to_excel(headers, rows, filepath)
            QMessageBox.information(self, "Trích xuất thành công", f"Dữ liệu lịch sử đã được lưu trữ.\n\n{result_msg}")
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi trích xuất", f"Không thể xuất báo cáo:\n{str(exc)}")