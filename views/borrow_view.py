"""Giao diện quản lý mượn/trả thiết bị."""

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView, QComboBox, QGroupBox,
    QSpinBox, QDateEdit, QTabWidget
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from controllers.borrow_controller import BorrowController
from controllers.user_controller import UserController
from controllers.equipment_controller import EquipmentController
from controllers.database_connection import DatabaseConnection
from models.borrow_detail import BorrowDetail
from models.borrow_record import BorrowRecord
from utils.validators import validate_borrow_cart
from views.theme import get_button_style


class BorrowView(QWidget):
    """Widget quản lý mượn/trả thiết bị với giao diện Flat Design."""

    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.borrow_controller = BorrowController()
        self.user_controller = UserController()
        self.equipment_controller = EquipmentController()
        self.cart_items = []
        
        self.user_role = str(self.current_user.role).lower() if (self.current_user and hasattr(self.current_user, 'role')) else 'user'
        
        self.init_ui()
        self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        title_label = QLabel("QUẢN LÝ MƯỢN TRẢ THIẾT BỊ")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addWidget(title_label)

        # Tab Widget tổng
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_borrow_tab(), "📥 Lập Phiếu Mượn")
        self.tabs.addTab(self._create_return_tab(), "📤 Trả Thiết Bị")
        
        if self.user_role == 'admin':
            self.tabs.addTab(self._create_approval_tab(), "✅ Phê Duyệt Phiếu")
        
        main_layout.addWidget(self.tabs)
        self.setLayout(main_layout)

    def _setup_flat_table(self, table: QTableWidget):
        """Hàm tiện ích để tối ưu hóa UI cho các bảng dữ liệu."""
        table.verticalHeader().setVisible(False)
        table.verticalHeader().setDefaultSectionSize(45)
        table.setFocusPolicy(Qt.NoFocus)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)

    def _create_borrow_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        form_group = QGroupBox("Thông tin đăng ký mượn")
        form_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 25, 20, 20)
        form_layout.setColumnStretch(0, 1)
        form_layout.setColumnStretch(1, 3)

        form_layout.addWidget(QLabel("Mã phiếu tự động:"), 0, 0)
        self.lbl_transaction_id = QLabel()
        self.lbl_transaction_id.setStyleSheet("font-weight: bold; color: #2563eb; font-size: 14px;")
        self.lbl_transaction_id.setText(self.borrow_controller.generate_record_id())
        form_layout.addWidget(self.lbl_transaction_id, 0, 1)

        form_layout.addWidget(QLabel("Người mượn:"), 1, 0)
        self.cmb_user = QComboBox()
        self.cmb_user.setMinimumWidth(300)
        form_layout.addWidget(self.cmb_user, 1, 1)

        form_layout.addWidget(QLabel("Ngày trả dự kiến:"), 2, 0)
        self.date_expected_return = QDateEdit()
        self.date_expected_return.setCalendarPopup(True)
        self.date_expected_return.setDate(QDate.currentDate().addDays(7))
        self.date_expected_return.setMinimumDate(QDate.currentDate())
        form_layout.addWidget(self.date_expected_return, 2, 1)

        form_layout.addWidget(QLabel("Chọn thiết bị:"), 3, 0)
        self.cmb_equipment = QComboBox()
        self.cmb_equipment.currentIndexChanged.connect(self._on_equipment_changed)
        form_layout.addWidget(self.cmb_equipment, 3, 1)

        # Hàng chứa thông tin Khả dụng và Số lượng nằm cạnh nhau để tiết kiệm không gian
        qty_layout = QHBoxLayout()
        qty_layout.addWidget(QLabel("Khả dụng trong kho:"))
        self.lbl_available = QLabel("0")
        self.lbl_available.setStyleSheet("font-weight: bold; color: #16a34a;")
        qty_layout.addWidget(self.lbl_available)
        
        qty_layout.addSpacing(20)
        qty_layout.addWidget(QLabel("Số lượng mượn:"))
        self.spin_borrow_qty = QSpinBox()
        self.spin_borrow_qty.setRange(1, 9999)
        self.spin_borrow_qty.setValue(1)
        qty_layout.addWidget(self.spin_borrow_qty)
        qty_layout.addStretch()
        form_layout.addLayout(qty_layout, 4, 1)

        self.btn_add_to_cart = QPushButton("Thêm vào danh sách mượn")
        self.btn_add_to_cart.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_add_to_cart.clicked.connect(self.add_item_to_cart)
        form_layout.addWidget(self.btn_add_to_cart, 5, 1, alignment=Qt.AlignLeft)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # Bảng giỏ hàng
        cart_label = QLabel("Danh sách thiết bị chờ tạo phiếu:")
        cart_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
        layout.addWidget(cart_label)

        self.table_cart = QTableWidget(0, 4)
        self.table_cart.setHorizontalHeaderLabels(["Mã thiết bị", "Tên thiết bị", "Số lượng", "Khả dụng"])
        self._setup_flat_table(self.table_cart)
        self.table_cart.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.table_cart)

        # Nút tương tác giỏ hàng
        action_layout = QHBoxLayout()
        self.btn_remove_cart = QPushButton("Xóa mục chọn")
        self.btn_remove_cart.setStyleSheet(get_button_style("danger", is_dark=False))
        self.btn_remove_cart.clicked.connect(self.remove_cart_item)
        action_layout.addWidget(self.btn_remove_cart)

        action_layout.addStretch()

        self.btn_reset_borrow = QPushButton("Làm mới form")
        self.btn_reset_borrow.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_reset_borrow.clicked.connect(self.reset_borrow_form)
        action_layout.addWidget(self.btn_reset_borrow)

        self.btn_create_borrow = QPushButton("Xác nhận Tạo phiếu")
        self.btn_create_borrow.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_create_borrow.clicked.connect(self.create_borrow)
        action_layout.addWidget(self.btn_create_borrow)

        layout.addLayout(action_layout)
        tab.setLayout(layout)
        return tab

    def _create_return_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        info_label = QLabel("Click chọn một Phiếu Mượn tổng quát ở bảng trên, sau đó chọn Thiết Bị cần trả ở bảng dưới.")
        info_label.setStyleSheet("font-style: italic; color: #64748b; margin-bottom: 5px;")
        layout.addWidget(info_label)

        # Bảng Phiếu Mượn Đang Active
        self.table_return = QTableWidget(0, 7)
        self.table_return.setHorizontalHeaderLabels([
            "Mã phiếu", "Người mượn", "Thiết bị tóm tắt", "Tổng SL", "Ngày mượn", "Hẹn trả", "Trạng thái"
        ])
        self._setup_flat_table(self.table_return)
        self.table_return.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table_return.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_return.itemSelectionChanged.connect(self._load_selected_record_details)
        layout.addWidget(self.table_return)

        layout.addWidget(QLabel("Chi tiết thiết bị thuộc Phiếu mượn đang chọn:"))

        # Bảng Chi tiết Thiết bị trong Phiếu
        self.details_table = QTableWidget(0, 5)
        self.details_table.setHorizontalHeaderLabels([
            "Mã CT", "Tên Thiết Bị", "Số Lượng", "Trạng Thái Giao Dịch", "Tình Trạng Kho"
        ])
        self._setup_flat_table(self.details_table)
        self.details_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.details_table)

        # Nút thao tác
        action_layout = QHBoxLayout()
        
        self.btn_return_selected = QPushButton("Trả thiết bị đã chọn")
        self.btn_return_selected.setStyleSheet(get_button_style("primary", is_dark=False))
        self.btn_return_selected.clicked.connect(self.return_selected_items)
        action_layout.addWidget(self.btn_return_selected)

        self.btn_return_all = QPushButton("Hoàn tất trả toàn bộ phiếu")
        self.btn_return_all.setStyleSheet(get_button_style("success", is_dark=False))
        self.btn_return_all.clicked.connect(self.return_all_items)
        action_layout.addWidget(self.btn_return_all)
        
        action_layout.addStretch()

        self.btn_refresh_return = QPushButton("Làm mới dữ liệu")
        self.btn_refresh_return.setStyleSheet(get_button_style("secondary", is_dark=False))
        self.btn_refresh_return.clicked.connect(self.load_active_records)
        action_layout.addWidget(self.btn_refresh_return)

        layout.addLayout(action_layout)
        tab.setLayout(layout)
        return tab

    def _create_approval_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        layout.addWidget(QLabel("Danh sách phiếu mượn chờ Admin kiểm duyệt:"))
        
        self.table_approval = QTableWidget(0, 7)
        self.table_approval.setHorizontalHeaderLabels([
            "Mã phiếu", "Người mượn", "Thiết bị", "Số lượng",
            "Ngày mượn", "Hẹn trả", "Trạng thái"
        ])
        self._setup_flat_table(self.table_approval)
        self.table_approval.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table_approval.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.table_approval)
        
        action_layout = QHBoxLayout()
        
        self.btn_approve = QPushButton("Phê duyệt và Xuất kho")
        self.btn_approve.setStyleSheet(get_button_style("success", is_dark=False))
        self.btn_approve.clicked.connect(self.approve_borrow)
        action_layout.addWidget(self.btn_approve)
        
        self.btn_reject = QPushButton("Từ chối phiếu")
        self.btn_reject.setStyleSheet(get_button_style("danger", is_dark=False))
        self.btn_reject.clicked.connect(self.reject_borrow)
        action_layout.addWidget(self.btn_reject)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        tab.setLayout(layout)
        return tab

    # ================= LOGIC DỮ LIỆU =================

    def _load_users_combo(self):
        try:
            users = self.user_controller.get_all_users()
            self.cmb_user.clear()
            
            if self.user_role == 'user' and self.current_user:
                user_id_val = getattr(self.current_user, 'user_id', getattr(self.current_user, 'id', None))
                full_name_val = getattr(self.current_user, 'full_name', 'Người dùng')
                if user_id_val:
                    self.cmb_user.addItem(f"{user_id_val} - {full_name_val}", user_id_val)
                self.cmb_user.setEnabled(False)
            else:
                for user in users:
                    user_id_val = getattr(user, 'user_id', getattr(user, 'id', None))
                    if user_id_val:
                        self.cmb_user.addItem(f"{user_id_val} - {user.full_name}", user_id_val)
                self.cmb_user.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi tải dữ liệu người dùng: {str(e)}")

    def _load_equipments_combo(self):
        try:
            equipments = self.equipment_controller.get_all_equipments()
            self.cmb_equipment.clear()
            for eq in equipments:
                self.cmb_equipment.addItem(f"{eq.equipment_id} - {eq.equipment_name}", eq.equipment_id)
            self._on_equipment_changed()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi tải dữ liệu thiết bị: {str(e)}")

    def _on_equipment_changed(self):
        equipment_id = self.cmb_equipment.currentData()
        if equipment_id:
            equipment = self.equipment_controller.get_equipment_by_id(equipment_id)
            if equipment:
                self.lbl_available.setText(str(equipment.available_quantity))
                self.spin_borrow_qty.setMaximum(max(1, equipment.available_quantity))
            else:
                self.lbl_available.setText("0")
                self.spin_borrow_qty.setMaximum(1)

    def add_item_to_cart(self):
        equipment_id = self.cmb_equipment.currentData()
        if equipment_id is None:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thiết bị.")
            return

        quantity = self.spin_borrow_qty.value()
        equipment = self.equipment_controller.get_equipment_by_id(equipment_id)
        if not equipment:
            QMessageBox.warning(self, "Cảnh báo", "Thiết bị không tồn tại.")
            return
        if quantity > equipment.available_quantity:
            QMessageBox.warning(self, "Cảnh báo", "Số lượng mượn vượt quá khả dụng.")
            return

        for item in self.cart_items:
            if item.device_id == equipment_id:
                item.quantity += quantity
                break
        else:
            self.cart_items.append(BorrowDetail(
                device_id=equipment_id,
                device_name=equipment.equipment_name,
                quantity=quantity
            ))
        self.refresh_cart_table()

    def refresh_cart_table(self):
        self.table_cart.setRowCount(0)
        for item in self.cart_items:
            row = self.table_cart.rowCount()
            self.table_cart.insertRow(row)
            self.table_cart.setItem(row, 0, QTableWidgetItem(str(item.device_id)))
            self.table_cart.setItem(row, 1, QTableWidgetItem(str(item.device_name)))
            self.table_cart.setItem(row, 2, QTableWidgetItem(str(item.quantity)))
            equipment = self.equipment_controller.get_equipment_by_id(item.device_id)
            self.table_cart.setItem(row, 3, QTableWidgetItem(str(equipment.available_quantity if equipment else 0)))

    def remove_cart_item(self):
        selected_items = self.table_cart.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn mục trong giỏ.")
            return
        row = self.table_cart.currentRow()
        device_id = self.table_cart.item(row, 0).text()
        self.cart_items = [item for item in self.cart_items if str(item.device_id) != device_id]
        self.refresh_cart_table()

    def reset_borrow_form(self):
        self.lbl_transaction_id.setText(self.borrow_controller.generate_record_id())
        if self.cmb_user.count() > 0:
            self.cmb_user.setCurrentIndex(0)
        self._load_equipments_combo()
        self.cart_items = []
        self.refresh_cart_table()
        self.date_expected_return.setDate(QDate.currentDate().addDays(7))

    def load_data(self):
        self._load_users_combo()
        self._load_equipments_combo()
        self.load_active_records()
        if self.user_role == 'admin':
            self.load_pending_approvals()

    def load_pending_approvals(self):
        try:
            results = self.borrow_controller.get_pending_approvals_data()
            self.table_approval.setRowCount(0)
            for row_data in results:
                row = self.table_approval.rowCount()
                self.table_approval.insertRow(row)
                self.table_approval.setItem(row, 0, QTableWidgetItem(str(row_data.get('record_id', ''))))
                self.table_approval.setItem(row, 1, QTableWidgetItem(str(row_data.get('user_id', ''))))
                self.table_approval.setItem(row, 2, QTableWidgetItem(str(row_data.get('device_name', ''))))
                self.table_approval.setItem(row, 3, QTableWidgetItem(str(row_data.get('quantity', ''))))
                self.table_approval.setItem(row, 4, QTableWidgetItem(str(row_data.get('borrow_date', ''))[:10]))
                self.table_approval.setItem(row, 5, QTableWidgetItem(str(row_data.get('expected_return_date', ''))[:10]))
                self.table_approval.setItem(row, 6, QTableWidgetItem(str(row_data.get('status', ''))))
        except Exception as e:
            pass

    def load_active_records(self):
        try:
            records = self.borrow_controller.get_active_records()
            self.table_return.setRowCount(0)
            for record in records:
                for detail in record.details:
                    row = self.table_return.rowCount()
                    self.table_return.insertRow(row)
                    self.table_return.setItem(row, 0, QTableWidgetItem(str(record.record_id)))
                    self.table_return.setItem(row, 1, QTableWidgetItem(str(record.user_id)))
                    self.table_return.setItem(row, 2, QTableWidgetItem(str(detail.device_name)))
                    self.table_return.setItem(row, 3, QTableWidgetItem(str(detail.quantity)))
                    self.table_return.setItem(row, 4, QTableWidgetItem(record.borrow_date.strftime('%d/%m/%Y') if record.borrow_date else ''))
                    self.table_return.setItem(row, 5, QTableWidgetItem(record.expected_return_date.strftime('%d/%m/%Y') if record.expected_return_date else ''))
                    
                    status_text = str(record.status)
                    status_item = QTableWidgetItem(status_text)
                    self.table_return.setItem(row, 6, status_item)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi nạp phiếu hiện hành: {str(e)}")

    def create_borrow(self):
        record_id = self.lbl_transaction_id.text()
        user_id = self.cmb_user.currentData()
        expected_date = self.date_expected_return.date().toPyDate()
        is_valid, error_msg = validate_borrow_cart(user_id, self.cart_items, expected_date)
        if not is_valid:
            QMessageBox.warning(self, "Cảnh báo", error_msg)
            return
        try:
            record = BorrowRecord(
                record_id=record_id, user_id=user_id, borrow_date=datetime.utcnow(),
                expected_return_date=datetime.combine(expected_date, datetime.min.time()),
                status='Chờ phê duyệt', details=self.cart_items,
            )
            self.borrow_controller.create_borrow_record(record, self.current_user)
            QMessageBox.information(self, "Thành công", "Tạo phiếu mượn thành công! Đang chờ phê duyệt.")
            self.reset_borrow_form()
            self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def approve_borrow(self):
        selected = self.table_approval.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Cảnh báo", "Chọn phiếu để phê duyệt.")
            return
        record_id = self.table_approval.item(self.table_approval.currentRow(), 0).text()
        try:
            success = self.borrow_controller.approve_pending_record(record_id)
            if success:
                QMessageBox.information(self, "Thành công", "Đã phê duyệt và xuất kho!")
                self.load_data()
            else:
                QMessageBox.critical(self, "Thất bại", "Phê duyệt thất bại. Kiểm tra lại tồn kho.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            
    def reject_borrow(self):
        selected = self.table_approval.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Cảnh báo", "Chọn phiếu để từ chối.")
            return
        record_id = self.table_approval.item(self.table_approval.currentRow(), 0).text()
        try:
            success = self.borrow_controller.reject_pending_record(record_id)
            if success:
                QMessageBox.information(self, "Thành công", "Đã từ chối phiếu mượn.")
                self.load_data()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def _load_selected_record_details(self):
        selected_items = self.table_return.selectedItems()
        if not selected_items:
            return
        record_id = self.table_return.item(self.table_return.currentRow(), 0).text()
        record = self.borrow_controller.get_record_by_id(record_id)
        if record:
            self.details_table.setRowCount(0)
            for detail in record.details:
                row = self.details_table.rowCount()
                self.details_table.insertRow(row)
                self.details_table.setItem(row, 0, QTableWidgetItem(str(detail.detail_id)))
                self.details_table.setItem(row, 1, QTableWidgetItem(str(detail.device_name)))
                self.details_table.setItem(row, 2, QTableWidgetItem(str(detail.quantity)))
                status_str = 'Đã trả' if getattr(detail, 'returned', False) else 'Chưa trả'
                self.details_table.setItem(row, 3, QTableWidgetItem(status_str))
                self.details_table.setItem(row, 4, QTableWidgetItem(status_str))

    def return_selected_items(self):
        selected_items = self.details_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Cảnh báo", "Chọn thiết bị trong bảng chi tiết để trả.")
            return
        record_id = self.table_return.item(self.table_return.currentRow(), 0).text()
        selected_rows = {item.row() for item in selected_items}
        detail_ids = [int(self.details_table.item(row, 0).text()) for row in selected_rows]
        try:
            self.borrow_controller.return_items(record_id, detail_ids)
            QMessageBox.information(self, "Thành công", "Đã trả các thiết bị được lựa chọn!")
            self.load_data()
            self._load_selected_record_details()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))

    def return_all_items(self):
        selected = self.table_return.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Cảnh báo", "Chọn một phiếu mượn tổng quát.")
            return
        record_id = self.table_return.item(self.table_return.currentRow(), 0).text()
        record = self.borrow_controller.get_record_by_id(record_id)
        if not record:
            return
        detail_ids = [detail.detail_id for detail in record.details if not getattr(detail, 'returned', False)]
        if not detail_ids:
            QMessageBox.information(self, "Thông báo", "Phiếu mượn này đã trả đầy đủ.")
            return
        try:
            self.borrow_controller.return_items(record_id, detail_ids)
            QMessageBox.information(self, "Thành công", "Đã thu hồi toàn bộ thiết bị thuộc đơn này!")
            self.load_data()
            self._load_selected_record_details()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))