"""Giao diện quản lý Thiết bị/Linh kiện."""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView, QSpinBox,
    QComboBox, QGroupBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from controllers.equipment_controller import EquipmentController
from models.equipment import Equipment
from utils.validators import validate_equipment_input
from views.theme import get_button_style


class EquipmentView(QWidget):
    """Widget quản lý thiết bị với chức năng CRUD và phản hồi trực quan."""

    def __init__(self):
        super().__init__()
        self.controller = EquipmentController()
        self.selected_equipment_id = None
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        
        # Mở rộng không gian hiển thị tổng thể
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Tiêu đề phân hệ
        title_label = QLabel("QUẢN LÝ KHO THIẾT BỊ VÀ LINH KIỆN")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(title_label)

        # --- Khu vực Form nhập liệu ---
        input_group = QGroupBox("Thông tin chi tiết thiết bị")
        input_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)

        form_layout.addWidget(QLabel("Mã thiết bị:"), 0, 0)
        self.txt_id = QLineEdit()
        self.txt_id.setPlaceholderText("VD: TB001")
        form_layout.addWidget(self.txt_id, 0, 1)

        form_layout.addWidget(QLabel("Tên thiết bị:"), 0, 2)
        self.txt_name = QLineEdit()
        self.txt_name.setPlaceholderText("Nhập tên thiết bị")
        form_layout.addWidget(self.txt_name, 0, 3)

        form_layout.addWidget(QLabel("Phân loại:"), 1, 0)
        self.cmb_category = QComboBox()
        self.cmb_category.addItems(["Cảm biến", "Vi điều khiển", "Dụng cụ đo", "Mô-đun", "Khác"])
        form_layout.addWidget(self.cmb_category, 1, 1)

        form_layout.addWidget(QLabel("Trạng thái:"), 1, 2)
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Có sẵn", "Đang được mượn", "Đang bảo trì", "Hỏng"])
        form_layout.addWidget(self.cmb_status, 1, 3)

        form_layout.addWidget(QLabel("Tổng số lượng:"), 2, 0)
        self.spin_total = QSpinBox()
        self.spin_total.setRange(0, 10000)
        form_layout.addWidget(self.spin_total, 2, 1)

        form_layout.addWidget(QLabel("Khả dụng:"), 2, 2)
        self.spin_available = QSpinBox()
        self.spin_available.setRange(0, 10000)
        form_layout.addWidget(self.spin_available, 2, 3)

        input_group.setLayout(form_layout)
        main_layout.addWidget(input_group)

        # --- Khu vực Nút bấm hành động và Tìm kiếm ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(12)
        
        self.btn_add = QPushButton("Thêm mới")
        self.btn_add.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_add.clicked.connect(self.add_equipment)
        
        self.btn_update = QPushButton("Cập nhật")
        self.btn_update.setStyleSheet(get_button_style("success", is_dark=False))
        self.btn_update.clicked.connect(self.update_equipment)
        
        self.btn_delete = QPushButton("Xóa")
        self.btn_delete.setStyleSheet(get_button_style("danger", is_dark=False))
        self.btn_delete.clicked.connect(self.delete_equipment)
        
        self.btn_clear = QPushButton("Làm mới form")
        self.btn_clear.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_clear.clicked.connect(self.clear_form)

        action_layout.addWidget(self.btn_add)
        action_layout.addWidget(self.btn_update)
        action_layout.addWidget(self.btn_delete)
        action_layout.addWidget(self.btn_clear)
        
        action_layout.addStretch() # Đẩy thanh tìm kiếm sang góc phải

        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Tìm kiếm theo mã hoặc tên...")
        self.txt_search.setMinimumWidth(300)
        self.txt_search.textChanged.connect(self.search_equipment)
        action_layout.addWidget(self.txt_search)

        main_layout.addLayout(action_layout)

        # --- Khu vực Bảng dữ liệu ---
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Mã TB", "Tên thiết bị", "Phân loại", 
            "Tổng SL", "Khả dụng", "Trạng thái"
        ])
        
        # Tối ưu hóa UI cho TableWidget
        self.table.verticalHeader().setVisible(False) 
        self.table.verticalHeader().setDefaultSectionSize(45) 
        self.table.setFocusPolicy(Qt.NoFocus) 
        self.table.setShowGrid(False) 
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Thiết lập tỷ lệ co giãn các cột hợp lý
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch) 
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.itemSelectionChanged.connect(self.on_select_row)
        main_layout.addWidget(self.table)

        # Trình xuất thông báo phản hồi (Inline Feedback)
        self.lbl_feedback = QLabel("")
        self.lbl_feedback.setAlignment(Qt.AlignCenter)
        self.lbl_feedback.setFont(QFont("Segoe UI", 10, QFont.Bold))
        main_layout.addWidget(self.lbl_feedback)

        self.setLayout(main_layout)

    def show_feedback(self, message, is_error=False):
        """Hiển thị phản hồi trạng thái tạm thời trên giao diện."""
        color = "#dc2626" if is_error else "#16a34a"
        self.lbl_feedback.setStyleSheet(f"color: {color}; padding: 5px;")
        self.lbl_feedback.setText(message)
        QTimer.singleShot(3000, lambda: self.lbl_feedback.setText(""))

    def load_data(self):
        try:
            equipments = self.controller.get_all_equipments()
            self._populate_table(equipments)
        except Exception as e:
            self.show_feedback(f"Lỗi truy xuất hệ thống: {str(e)}", is_error=True)

    def _populate_table(self, equipments):
        self.table.setRowCount(0)
        for eq in equipments:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Tương thích đọc dữ liệu dạng Object hoặc Dictionary
            eq_id = getattr(eq, 'equipment_id', getattr(eq, 'id', ''))
            eq_name = getattr(eq, 'equipment_name', getattr(eq, 'name', ''))
            eq_cat = getattr(eq, 'category', '')
            eq_total = getattr(eq, 'total_quantity', getattr(eq, 'total_qty', 0))
            eq_avail = getattr(eq, 'available_quantity', getattr(eq, 'available_qty', 0))
            eq_status = getattr(eq, 'status', '')
            
            self.table.setItem(row, 0, QTableWidgetItem(str(eq_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(eq_name)))
            self.table.setItem(row, 2, QTableWidgetItem(str(eq_cat)))
            self.table.setItem(row, 3, QTableWidgetItem(str(eq_total)))
            self.table.setItem(row, 4, QTableWidgetItem(str(eq_avail)))
            self.table.setItem(row, 5, QTableWidgetItem(str(eq_status)))

    def on_select_row(self):
        selected = self.table.selectedItems()
        if not selected:
            return
        row = selected[0].row()
        self.selected_equipment_id = self.table.item(row, 0).text()
        
        self.txt_id.setText(self.selected_equipment_id)
        self.txt_name.setText(self.table.item(row, 1).text())
        self.cmb_category.setCurrentText(self.table.item(row, 2).text())
        self.spin_total.setValue(int(self.table.item(row, 3).text()))
        self.spin_available.setValue(int(self.table.item(row, 4).text()))
        self.cmb_status.setCurrentText(self.table.item(row, 5).text())

        # Khóa ID không cho sửa đổi khi đang chọn
        self.txt_id.setReadOnly(True)

    def get_form_data(self):
        return {
            'equipment_id': self.txt_id.text().strip(),
            'name': self.txt_name.text().strip(),
            'category': self.cmb_category.currentText(),
            'total_qty': self.spin_total.value(),
            'available_qty': self.spin_available.value(),
            'status': self.cmb_status.currentText()
        }

    def clear_form(self):
        self.selected_equipment_id = None
        self.txt_id.clear()
        self.txt_id.setReadOnly(False)
        self.txt_name.clear()
        self.cmb_category.setCurrentIndex(0)
        self.spin_total.setValue(0)
        self.spin_available.setValue(0)
        self.cmb_status.setCurrentIndex(0)
        self.table.clearSelection()

    def add_equipment(self):
        data = self.get_form_data()
        is_valid, msg = validate_equipment_input(**data)
        if not is_valid:
            self.show_feedback(msg, is_error=True)
            return
        try:
            eq = Equipment(
                equipment_id=data['equipment_id'], 
                equipment_name=data['name'], 
                category=data['category'], 
                total_quantity=data['total_qty'], 
                available_quantity=data['available_qty'], 
                status=data['status']
            )
            self.controller.create_equipment(eq)
            self.show_feedback("Ghi nhận thiết bị mới thành công.")
            self.load_data()
            self.clear_form()
        except Exception as e:
            self.show_feedback(f"Từ chối thao tác: {str(e)}", is_error=True)

    def update_equipment(self):
        if not self.selected_equipment_id:
            self.show_feedback("Từ chối: Chưa chọn thiết bị đích.", is_error=True)
            return
            
        data = self.get_form_data()
        is_valid, msg = validate_equipment_input(**data)
        if not is_valid:
            self.show_feedback(msg, is_error=True)
            return
            
        try:
            eq = Equipment(
                equipment_id=data['equipment_id'], 
                equipment_name=data['name'], 
                category=data['category'], 
                total_quantity=data['total_qty'], 
                available_quantity=data['available_qty'], 
                status=data['status']
            )
            self.controller.update_equipment(eq)
            self.show_feedback("Lưu thiết lập cập nhật thành công.")
            self.load_data()
            self.clear_form()
        except Exception as e:
            self.show_feedback(f"Lỗi xung đột dữ liệu: {str(e)}", is_error=True)

    def delete_equipment(self):
        if not self.selected_equipment_id:
            self.show_feedback("Từ chối: Chưa chọn thiết bị đích.", is_error=True)
            return

        reply = QMessageBox.question(
            self,
            "Xác nhận vô hiệu hóa",
            f"Thao tác này loại bỏ thiết bị '{self.selected_equipment_id}' khỏi hệ thống. Tiếp tục?",
            QMessageBox.Yes | QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            try:
                self.controller.delete_equipment(self.selected_equipment_id)
                self.show_feedback("Đã loại bỏ thiết bị khỏi cơ sở dữ liệu.")
                self.load_data()
                self.clear_form()
            except Exception as e:
                self.show_feedback(f"Từ chối thao tác: Dữ liệu đang được liên kết ({str(e)})", is_error=True)

    def search_equipment(self):
        keyword = self.txt_search.text().strip()
        try:
            if keyword:
                equipments = self.controller.search_equipments(keyword)
            else:
                equipments = self.controller.get_all_equipments()
            self._populate_table(equipments)
        except Exception as e:
            self.show_feedback(f"Lỗi truy vấn tìm kiếm: {str(e)}", is_error=True)