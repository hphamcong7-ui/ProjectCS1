"""
Cửa sổ chính của ứng dụng - Đã phân quyền và tích hợp thông báo, hóa đơn
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QStatusBar, QMenuBar, QMenu, QAction,
    QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QIcon

from views.equipment_view import EquipmentView
from views.user_view import UserView
from views.borrow_view import BorrowView
from views.theme import get_stylesheet
from controllers.borrow_controller import BorrowController
from controllers.report_controller import ReportController

class MainWindow(QMainWindow):
    def __init__(self, current_user=None):
        super().__init__()
        self.current_user = current_user
        self.is_dark_mode = False
        self.borrow_controller = BorrowController()
        self.report_controller = ReportController()
        
        # Kiểm tra thuộc tính phân quyền bắt buộc
        if not hasattr(self.current_user, 'role'):
            # Fallback nếu object không có thuộc tính role
            self.user_role = 'user'
        else:
            self.user_role = self.current_user.role.lower()

        self.init_ui()
        self._setup_timers()
    
    def _setup_timers(self):
        """Thiết lập hệ thống kiểm tra và thông báo tự động định kỳ."""
        # Kiểm tra phiếu mượn sắp đến hạn hoặc quá hạn (Mỗi 15 phút quét 1 lần)
        self.check_overdue_timer = QTimer(self)
        self.check_overdue_timer.timeout.connect(self._check_overdue_notifications)
        self.check_overdue_timer.start(15 * 60 * 1000)  # 15 phút
        
        # Trigger kiểm tra ngay khi vừa khởi động ứng dụng sau 2 giây
        QTimer.singleShot(2000, self._check_overdue_notifications)
    
    def _check_overdue_notifications(self):
        """Quét dữ liệu và phát cảnh báo trực quan cho Admin hoặc User hiện tại."""
        try:
            # Gọi phương thức từ controller trả về danh sách chuỗi cảnh báo mẫu
            # Hàm này lọc theo user_id nếu là 'user' và trả về toàn bộ nếu là 'admin'
            alerts = self.borrow_controller.get_due_alerts(self.current_user)
            if alerts:
                # Hiển thị hộp thoại cảnh báo tập trung
                QMessageBox.warning(
                    self, 
                    "Hệ thống Cảnh báo Hạn trả", 
                    "Phát hiện các đơn mượn sắp đến hạn hoặc quá hạn:\n\n" + "\n".join(alerts)
                )
        except Exception as e:
            print(f"Lỗi hệ thống khi quét thông báo tự động: {e}")
    
    def init_ui(self):
        title_text = "Hệ thống Quản lý Linh kiện và Thiết bị Phòng Thí nghiệm"
        if self.current_user and hasattr(self.current_user, 'full_name'):
            title_text += f" - {self.current_user.full_name}"
        self.setWindowTitle(title_text)
        self.setGeometry(100, 100, 1200, 700)
        self.setMinimumSize(1000, 600)
        
        # Khởi tạo thanh thực đơn hành động
        self._create_menu_bar()
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header_label = QLabel("HỆ THỐNG QUẢN LÝ LINH KIỆN VÀ THIẾT BỊ PHÒNG THÍ NGHIỆM")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setObjectName("appHeader")
        main_layout.addWidget(header_label)
        
        # Khởi tạo Widget điều hướng dạng Tab
        self.tabs = QTabWidget()
        
        # --- BẮT ĐẦU PHÂN CHIA GIAO DIỆN THEO QUYỀN TRUY CẬP ---
        if self.user_role == 'admin':
            # Admin có toàn quyền quản lý hệ thống dữ liệu, thiết bị và con người
            self.equipment_view = EquipmentView()
            self.user_view = UserView()
            self.borrow_view = BorrowView(self.current_user) # Tích hợp chức năng mượn nhiều thiết bị (Cart)
            
            self.tabs.addTab(self.borrow_view, "Quản lý Mượn/Trả Thiết Bị")
            self.tabs.addTab(self.equipment_view, "Kho Linh Kiện & Thiết Bị")
            self.tabs.addTab(self.user_view, "Hồ sơ Người dùng (Tài khoản)")
        else:
            # Phân hệ dành riêng cho User/Người mượn phổ thông: Bị cô lập hoàn toàn khỏi Tab quản lý cấu hình
            self.borrow_view = BorrowView(self.current_user)
            self.tabs.addTab(self.borrow_view, "Đăng ký Mượn & Trả Thiết Bị")
        # --- KẾT THÚC PHÂN CHIA GIAO DIỆN ---
        
        main_layout.addWidget(self.tabs)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Hiển thị trạng thái phiên làm việc dưới thanh Status Bar
        if self.current_user and hasattr(self.current_user, 'full_name'):
            self.statusBar().showMessage(
                f"Tài khoản: {self.current_user.full_name} | Quyền hạn: {self.user_role.upper()} | Kết nối cơ sở dữ liệu ổn định."
            )
        else:
            self.statusBar().showMessage("Sẵn sàng")
        self._apply_styles()
    
    def _create_menu_bar(self):
        menubar = self.menuBar()
        system_menu = menubar.addMenu("Hệ thống")
        
        refresh_action = QAction("Làm mới dữ liệu", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_all)
        system_menu.addAction(refresh_action)
        
        system_menu.addSeparator()
        
        logout_action = QAction("Đăng xuất", self)
        logout_action.setShortcut("Ctrl+L")
        logout_action.triggered.connect(self._logout)
        system_menu.addAction(logout_action)
        
        system_menu.addSeparator()
        
        exit_action = QAction("Thoát", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        system_menu.addAction(exit_action)

        # --- MENU BỔ SUNG: DÀNH RIÊNG CHO TÍNH NĂNG BÁO CÁO & XUẤT HÓA ĐƠN ---
        report_menu = menubar.addMenu("Báo cáo & In ấn")
        
        invoice_action = QAction("Xuất hóa đơn chi tiết đơn mượn...", self)
        invoice_action.triggered.connect(self._export_specific_invoice)
        report_menu.addAction(invoice_action)
        
        # Giới hạn chức năng in toàn bộ danh sách người mượn: Chỉ cho phép tài khoản Admin thực hiện
        if self.user_role == 'admin':
            report_menu.addSeparator()
            borrowers_list_action = QAction("In danh sách tổng hợp người mượn (CSV)", self)
            borrowers_list_action.triggered.connect(self._export_borrowers_list)
            report_menu.addAction(borrowers_list_action)
        # ---------------------------------------------------------------------

        view_menu = menubar.addMenu("Giao diện")
        toggle_theme_action = QAction("Đổi chế độ Sáng/Tối", self)
        toggle_theme_action.setShortcut("F12")
        toggle_theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(toggle_theme_action)
        
        help_menu = menubar.addMenu("Trợ giúp")
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _export_specific_invoice(self):
        """Hộp thoại yêu cầu nhập ID đơn mượn để tiến hành xuất hóa đơn vật lý ra file CSV."""
        record_id, ok = QInputDialog.getInt(self, "Xuất hóa đơn", "Nhập mã số đơn mượn (Record ID):", min=1)
        if ok:
            try:
                # Thực thi xuất dữ liệu qua ReportController
                success = self.report_controller.export_invoice_to_csv(record_id)
                if success:
                    QMessageBox.information(self, "Thành công", f"Đã xuất hóa đơn của đơn mượn #{record_id} thành công ra file CSV.")
                else:
                    QMessageBox.warning(self, "Thất bại", f"Không tìm thấy dữ liệu hoặc không thể ghi file cho đơn mượn #{record_id}.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Quá trình trích xuất hóa đơn xảy ra lỗi: {e}")

    def _export_borrowers_list(self):
        """Xuất danh sách tất cả những người đang mượn thiết bị trong hệ thống."""
        try:
            success = self.report_controller.export_borrowers_list_to_csv()
            if success:
                QMessageBox.information(self, "Thành công", "Đã kết xuất danh sách tổng hợp tất cả người mượn hiện hành ra file CSV.")
            else:
                QMessageBox.warning(self, "Thông báo", "Hiện tại không có dữ liệu người mượn chưa trả trong hệ thống.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", f"Không thể xuất danh sách người mượn: {e}")

    def _apply_styles(self):
        """Áp dụng style dựa trên trạng thái is_dark_mode"""
        self.setStyleSheet(get_stylesheet(self.is_dark_mode))
    
    def _toggle_theme(self):
        """Đảo ngược trạng thái và áp dụng lại style"""
        self.is_dark_mode = not self.is_dark_mode
        self._apply_styles()
        mode_name = "Tối" if self.is_dark_mode else "Sáng"
        self.statusBar().showMessage(f"Đã chuyển sang chế độ {mode_name}", 3000)

    def _refresh_all(self):
        """Làm mới tất cả dữ liệu các phân hệ đang hiển thị"""
        try:
            self.borrow_view.load_data()
            if self.user_role == 'admin':
                self.equipment_view.load_data()
                self.user_view.load_data()
            self.statusBar().showMessage("Đã đồng bộ và làm mới toàn bộ dữ liệu hệ thống", 3000)
        except Exception as e:
            print(f"Lỗi khi thực hiện làm mới dữ liệu: {e}")

    def _show_about(self):
        """Hiển thị thông tin về ứng dụng"""
        QMessageBox.about(
            self,
            "Giới thiệu",
            """
            <h3>Hệ thống Quản lý Linh kiện và Thiết bị Phòng Thí Nghiệm</h3>
            <p>Phiên bản nâng cấp: 2.0 (Hỗ trợ Giỏ hàng đa thiết bị & Phân quyền logic)</p>
            <p>Đồ án môn học - Phát triển ứng dụng Desktop</p>
            <p>Kiến trúc tiêu chuẩn: 3-Tier (Model - View - Controller)</p>
            <hr>
            <p>Công nghệ cốt lõi:</p>
            <ul>
                <li>Python 3.x / PyQt5 Giao diện</li>
                <li>SQLite3 Cơ sở dữ liệu quan hệ (Hỗ trợ Transaction)</li>
                <li>Kiểm soát luồng nghiệp vụ tập trung</li>
            </ul>
            """
        )

    def _logout(self):
        """Đăng xuất và quay lại màn hình đăng nhập"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn đăng xuất khỏi phiên làm việc hiện tại?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()

    def closeEvent(self, event):
        """Xử lý sự kiện đóng cửa sổ ứng dụng an toàn"""
        reply = QMessageBox.question(
            self,
            "Xác nhận",
            "Bạn có chắc muốn thoát ứng dụng? Mọi tiến trình chạy ngầm sẽ bị chấm dứt.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()