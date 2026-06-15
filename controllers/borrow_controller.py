"""Controller xử lý các thao tác Mượn/Trả thiết bị."""

from datetime import datetime, timedelta

from controllers.database_connection import DatabaseConnection
from controllers.equipment_controller import EquipmentController
from controllers.notification_controller import NotificationController
from controllers.user_controller import UserController
from models.borrow_detail import BorrowDetail
from models.borrow_record import BorrowRecord


class BorrowController:
    """Xử lý nghiệp vụ mượn/trả, báo cáo và thống kê."""

    def __init__(self):
        self.db = DatabaseConnection()
        self.equipment_controller = EquipmentController()
        self.user_controller = UserController()
        self.notification_controller = NotificationController()

    def generate_record_id(self):
        query = "SELECT record_id FROM borrow_records ORDER BY record_id DESC LIMIT 1"
        result = self.db.execute_query(query)
        if result:
            last_id = result[0]['record_id']
            if last_id.startswith('BR') and last_id[2:].isdigit():
                return f"BR{int(last_id[2:]) + 1:04d}"
        return f"BR{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    def create_borrow_record(self, record: BorrowRecord, current_user=None):
        if not record.details:
            raise Exception("Vui lòng chọn ít nhất một thiết bị để mượn.")

        user = self.user_controller.get_user_by_id(record.user_id)
        if not user:
            raise Exception(f"Không tìm thấy người dùng '{record.user_id}'.")

        if record.expected_return_date is None:
            raise Exception("Vui lòng nhập ngày trả dự kiến.")

        if record.expected_return_date <= record.borrow_date:
            raise Exception("Ngày trả dự kiến phải sau ngày mượn.")

        if current_user and current_user.role == 'User' and current_user.user_id != record.user_id:
            raise Exception("Bạn chỉ có thể tạo phiếu mượn cho chính mình.")

        record_id = record.record_id or self.generate_record_id()
        record.record_id = record_id
        
        # Mặc định ban đầu đưa về Chờ phê duyệt để đảm bảo an toàn kho báu dữ liệu
        record.status = 'Chờ phê duyệt'

        # Kiểm tra trước toàn bộ điều kiện của thiết bị trong giỏ hàng để tránh lỗi logic nửa chừng
        for detail in record.details:
            equipment = self.equipment_controller.get_equipment_by_id(detail.device_id)
            if not equipment:
                raise Exception(f"Không tìm thấy thiết bị '{detail.device_id}'.")
            if equipment.status == 'Đang bảo trì':
                raise Exception(f"Thiết bị '{equipment.equipment_name}' đang bảo trì và không thể mượn.")
            if detail.quantity > equipment.available_quantity:
                raise Exception(
                    f"Số lượng mượn của '{equipment.equipment_name}' vượt quá khả dụng ({equipment.available_quantity})."
                )

        insert_record = """
            INSERT INTO borrow_records
            (record_id, user_id, borrow_date, expected_return_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            record.record_id,
            record.user_id,
            record.borrow_date.isoformat() if hasattr(record.borrow_date, 'isoformat') else str(record.borrow_date),
            record.expected_return_date.isoformat() if hasattr(record.expected_return_date, 'isoformat') else str(record.expected_return_date),
            record.status,
            record.notes,
        )
        self.db.execute_non_query(insert_record, params)

        for detail in record.details:
            insert_detail = """
                INSERT INTO borrow_details
                (record_id, device_id, quantity, returned)
                VALUES (?, ?, ?, 0)
            """
            self.db.execute_non_query(
                insert_detail,
                (record.record_id, detail.device_id, detail.quantity),
            )

        # Phát tín hiệu hệ thống thông báo
        self.notification_controller.create_notification(
            title="Yêu cầu mượn chờ phê duyệt",
            message=f"Người dùng {user.full_name} đã tạo phiếu mượn {record.record_id}. Cần phê duyệt.",
            user_id=None,
            type_='admin',
        )
        self.notification_controller.create_notification(
            title="Phiếu mượn chờ phê duyệt",
            message=f"Phiếu {record.record_id} đã được tạo và chờ quản trị viên phê duyệt.",
            user_id=record.user_id,
            type_='info',
        )
        return record.record_id

    # --- CÁC PHƯƠNG THỨC BỔ SUNG KẾT NỐI HỆ THỐNG GIAO DIỆN MỚI ---

    def get_pending_approvals_data(self):
        """Lấy danh sách thô dưới dạng danh sách từ điển để nạp vào bảng phê duyệt của Admin."""
        query = """
            SELECT br.record_id, br.user_id, br.borrow_date, br.expected_return_date,
                   br.status, bd.device_id, bd.quantity, d.device_name
            FROM borrow_records br
            JOIN borrow_details bd ON br.record_id = bd.record_id
            JOIN devices d ON bd.device_id = d.device_id
            WHERE br.status = 'Chờ phê duyệt'
            ORDER BY br.borrow_date DESC
        """
        results = self.db.execute_query(query)
        return [dict(row) for row in results] if results else []

    def approve_pending_record(self, record_id):
        """Phê duyệt phiếu mượn, thực hiện trừ kho và chuyển trạng thái đồng loạt."""
        record = self.get_record_by_id(record_id)
        if not record:
            return False
            
        try:
            # 1. Cập nhật trạng thái phiếu mượn tổng
            self.db.execute_non_query(
                "UPDATE borrow_records SET status = 'Đang mượn' WHERE record_id = ?", 
                (record_id,)
            )
            
            # 2. Khấu trừ số lượng tồn kho khả dụng của từng thiết bị trong đơn mượn
            for detail in record.details:
                equipment = self.equipment_controller.get_equipment_by_id(detail.device_id)
                if equipment:
                    new_available = max(0, equipment.available_quantity - detail.quantity)
                    new_status = 'Đang được mượn' if new_available == 0 else equipment.status
                    self.db.execute_non_query(
                        "UPDATE devices SET available_quantity = ?, status = ? WHERE device_id = ?",
                        (new_available, new_status, detail.device_id)
                    )
            
            # 3. Gửi thông báo thành công tới người mượn
            self.notification_controller.create_notification(
                title="Phiếu mượn được phê duyệt",
                message=f"Phiếu {record_id} của bạn đã được quản trị viên phê duyệt. Hãy tới nhận thiết bị.",
                user_id=record.user_id,
                type_='success'
            )
            return True
        except Exception as e:
            print(f"Lỗi phê duyệt trong Controller: {e}")
            return False

    def reject_pending_record(self, record_id):
        """Từ chối phê duyệt đơn mượn và giải phóng trạng thái chờ."""
        record = self.get_record_by_id(record_id)
        if not record:
            return False
        try:
            self.db.execute_non_query(
                "UPDATE borrow_records SET status = 'Bị từ chối' WHERE record_id = ?", 
                (record_id,)
            )
            self.notification_controller.create_notification(
                title="Phiếu mượn bị từ chối",
                message=f"Phiếu mượn {record_id} của bạn đã bị từ chối phê duyệt.",
                user_id=record.user_id,
                type_='error'
            )
            return True
        except Exception as e:
            print(f"Lỗi từ chối phiếu mượn trong Controller: {e}")
            return False

    def get_due_alerts(self, current_user):
        """Quét tìm và xây dựng chuỗi cảnh báo hạn trả thiết bị linh hoạt theo quyền tài khoản."""
        now = datetime.utcnow()
        three_days_later = now + timedelta(days=3)
        
        # Chỉ quét các đơn chưa hoàn thành nghĩa vụ trả
        query = """
            SELECT br.record_id, br.user_id, br.expected_return_date, u.full_name
            FROM borrow_records br
            JOIN users u ON br.user_id = u.user_id
            WHERE br.status IN ('Đã phê duyệt', 'Đang mượn', 'Quá hạn')
            AND br.expected_return_date <= ?
        """
        params = [three_days_later.isoformat()]
        
        # Phân quyền lọc dữ liệu thông báo
        if current_user and current_user.role.lower() != 'admin':
            query += " AND br.user_id = ?"
            params.append(current_user.user_id)
            
        results = self.db.execute_query(query, tuple(params))
        alerts = []
        for row in results:
            exp_date = datetime.fromisoformat(row['expected_return_date'])
            prefix = "[QUÁ HẠN]" if exp_date < now else "[SẮP ĐẾN HẠN]"
            alerts.append(f"{prefix} Mã đơn: {row['record_id']} | Tài khoản: {row['full_name']} | Hạn trả: {exp_date.strftime('%d/%m/%Y')}")
        return alerts

    # --------------------------------------------------------------

    def get_all_records(self):
        query = """
            SELECT br.record_id, br.user_id, br.borrow_date, br.expected_return_date,
                   br.actual_return_date, br.status, br.notes,
                   bd.detail_id, bd.device_id, d.device_name, bd.quantity,
                   bd.returned, bd.return_date, bd.condition_on_return
            FROM borrow_records br
            JOIN borrow_details bd ON br.record_id = bd.record_id
            JOIN devices d ON bd.device_id = d.device_id
            ORDER BY br.borrow_date DESC, br.record_id DESC
        """
        return self._build_records(query)

    def get_active_records(self):
        query = """
            SELECT br.record_id, br.user_id, br.borrow_date, br.expected_return_date,
                   br.actual_return_date, br.status, br.notes,
                   bd.detail_id, bd.device_id, d.device_name, bd.quantity,
                   bd.returned, bd.return_date, bd.condition_on_return
            FROM borrow_records br
            JOIN borrow_details bd ON br.record_id = bd.record_id
            JOIN devices d ON bd.device_id = d.device_id
            WHERE br.status IN ('Đã phê duyệt', 'Đang mượn', 'Quá hạn')
            ORDER BY br.borrow_date DESC, br.record_id DESC
        """
        return self._build_records(query)
    
    def check_overdue_notifications(self):
        now = datetime.utcnow()
        twelve_hours_ago = now - timedelta(hours=12)
        
        query = """
            SELECT br.record_id, br.user_id, br.expected_return_date, u.full_name
            FROM borrow_records br
            JOIN users u ON br.user_id = u.user_id
            WHERE br.status IN ('Đã phê duyệt', 'Đang mượn')
            AND br.expected_return_date <= ?
            AND br.expected_return_date > ?
        """
        results = self.db.execute_query(query, (now.isoformat(), twelve_hours_ago.isoformat()))
        
        for row in results:
            record_id = row['record_id']
            user_id = row['user_id']
            user_name = row['full_name']
            
            self.notification_controller.create_notification(
                title="Cảnh báo: Quá hạn trả thiết bị",
                message=f"Phiếu mượn {record_id} của {user_name} sắp hết hạn trả (cách hạn dưới 12 tiếng).",
                user_id=None,
                type_='warning',
            )
            self.notification_controller.create_notification(
                title="Cảnh báo: Quá hạn trả",
                message=f"Phiếu mượn {record_id} của bạn sắp hết hạn trả. Vui lòng trả thiết bị sớm.",
                user_id=user_id,
                type_='warning',
            )

    def get_record_by_id(self, record_id):
        query = """
            SELECT br.record_id, br.user_id, br.borrow_date, br.expected_return_date,
                   br.actual_return_date, br.status, br.notes,
                   bd.detail_id, bd.device_id, d.device_name, bd.quantity,
                   bd.returned, bd.return_date, bd.condition_on_return
            FROM borrow_records br
            JOIN borrow_details bd ON br.record_id = bd.record_id
            JOIN devices d ON bd.device_id = d.device_id
            WHERE br.record_id = ?
        """
        records = self._build_records(query, (record_id,))
        return records[0] if records else None

    def _build_records(self, query, params=None):
        results = self.db.execute_query(query, params)
        records = {}
        for row in results:
            record_id = row['record_id']
            if record_id not in records:
                records[record_id] = BorrowRecord(
                    record_id=record_id,
                    user_id=row['user_id'],
                    borrow_date=datetime.fromisoformat(row['borrow_date']),
                    expected_return_date=datetime.fromisoformat(row['expected_return_date']),
                    actual_return_date=(datetime.fromisoformat(row['actual_return_date']) if row['actual_return_date'] else None),
                    status=row['status'],
                    notes=row['notes'] or '',
                    details=[],
                )
            detail = BorrowDetail(
                detail_id=row['detail_id'],
                record_id=record_id,
                device_id=row['device_id'],
                device_name=row['device_name'],
                quantity=row['quantity'],
                returned=row['returned'],
                return_date=(datetime.fromisoformat(row['return_date']) if row['return_date'] else None),
                condition_on_return=row['condition_on_return'] or '',
            )
            records[record_id].details.append(detail)
        return list(records.values())

    def return_items(self, record_id, detail_ids=None, condition='Tốt'):
        if not detail_ids:
            raise Exception("Vui lòng chọn thiết bị cần trả.")

        record = self.get_record_by_id(record_id)
        if not record:
            raise Exception(f"Không tìm thấy phiếu mượn {record_id}.")

        returning_details = [d for d in record.details if d.detail_id in detail_ids]
        if not returning_details:
            raise Exception("Không có thiết bị phù hợp để trả.")

        for detail in returning_details:
            if detail.returned:
                raise Exception(f"Thiết bị {detail.device_name} đã được trả trước đó.")

        for detail in returning_details:
            self.db.execute_non_query(
                """
                    UPDATE borrow_details
                    SET returned = 1, return_date = ?, condition_on_return = ?
                    WHERE detail_id = ?
                """,
                (datetime.utcnow().isoformat(), condition, detail.detail_id),
            )
            equipment = self.equipment_controller.get_equipment_by_id(detail.device_id)
            if equipment:
                new_available = equipment.available_quantity + detail.quantity
                new_status = equipment.status
                if equipment.status != 'Đang bảo trì':
                    new_status = 'Có sẵn' if new_available > 0 else 'Đang được mượn'
                self.db.execute_non_query(
                    "UPDATE devices SET available_quantity = ?, status = ? WHERE device_id = ?",
                    (new_available, new_status, detail.device_id),
                )

        pending = self.db.execute_query(
            "SELECT COUNT(*) AS cnt FROM borrow_details WHERE record_id = ? AND returned = 0",
            (record_id,),
        )
        all_returned = pending[0]['cnt'] == 0
        if all_returned:
            self.db.execute_non_query(
                "UPDATE borrow_records SET actual_return_date = ?, status = 'Đã trả' WHERE record_id = ?",
                (datetime.utcnow().isoformat(), record_id),
            )
            status_message = 'Đã trả'
        else:
            self.db.execute_non_query(
                "UPDATE borrow_records SET status = 'Đang mượn' WHERE record_id = ?",
                (record_id,),
            )
            status_message = 'Đang mượn'

        self.notification_controller.create_notification(
            title="Trả thiết bị",
            message=f"Phiếu {record_id} đã trả {'toàn bộ' if all_returned else 'một phần'}.",
            user_id=record.user_id,
            type_='success',
        )
        self.notification_controller.create_notification(
            title="Thiết bị đã được trả",
            message=f"Phiếu {record_id} đã cập nhật trạng thái {status_message}.",
            user_id=None,
            type_='admin',
        )

    def check_overdue_records(self):
        now = datetime.utcnow().date()
        overdue_query = """
            SELECT record_id, user_id, expected_return_date
            FROM borrow_records
            WHERE status = 'Đang mượn'
        """
        records = self.db.execute_query(overdue_query)
        for row in records:
            expected = datetime.fromisoformat(row['expected_return_date']).date()
            if expected < now:
                self.db.execute_non_query(
                    "UPDATE borrow_records SET status = 'Quá hạn' WHERE record_id = ?",
                    (row['record_id'],),
                )
                self._create_overdue_notification(row['record_id'], row['user_id'])

        due_soon_query = """
            SELECT record_id, user_id, expected_return_date
            FROM borrow_records
            WHERE status = 'Đang mượn'
        """
        records = self.db.execute_query(due_soon_query)
        warning_date = now + timedelta(days=3)
        for row in records:
            expected = datetime.fromisoformat(row['expected_return_date']).date()
            if now <= expected <= warning_date:
                self._create_due_soon_notification(row['record_id'], row['user_id'], expected)

    def _create_overdue_notification(self, record_id, user_id):
        message = f"Phiếu {record_id} đã quá hạn trả. Vui lòng kiểm tra và xử lý ngay."
        if not self._notification_exists('Quá hạn', message, user_id):
            self.notification_controller.create_notification(
                title='Quá hạn',
                message=message,
                user_id=user_id,
                type_='warning',
            )
            self.notification_controller.create_notification(
                title='Thiết bị quá hạn',
                message=message,
                user_id=None,
                type_='admin',
            )

    def _create_due_soon_notification(self, record_id, user_id, expected_date):
        message = f"Phiếu {record_id} sẽ đến hạn trả vào {expected_date.strftime('%d/%m/%Y')}"
        if not self._notification_exists('Sắp đến hạn', message, user_id):
            self.notification_controller.create_notification(
                title='Sắp đến hạn',
                message=message,
                user_id=user_id,
                type_='info',
            )

    def _notification_exists(self, title, message, user_id):
        query = """
            SELECT COUNT(*) AS cnt
            FROM notifications
            WHERE title = ? AND message = ? AND user_id IS ?
        """
        result = self.db.execute_query(query, (title, message, user_id))
        return result and result[0]['cnt'] > 0

    def get_dashboard_metrics(self):
        metrics = {}
        total_devices = self.db.execute_query("SELECT COUNT(*) AS cnt FROM devices")[0]['cnt']
        borrowed_items = self.db.execute_query(
            "SELECT SUM(quantity) AS cnt FROM borrow_details WHERE returned = 0"
        )[0]['cnt'] or 0
        available_items = self.db.execute_query(
            "SELECT SUM(available_quantity) AS cnt FROM devices")[0]['cnt'] or 0
        overdue_records = self.db.execute_query(
            "SELECT COUNT(*) AS cnt FROM borrow_records WHERE status = 'Quá hạn'"
        )[0]['cnt']
        metrics['total_devices'] = total_devices
        metrics['borrowed_items'] = borrowed_items
        metrics['available_items'] = available_items
        metrics['overdue_records'] = overdue_records
        return metrics

    def get_statistics(self):
        stats = {}
        most_borrowed = self.db.execute_query(
            """
            SELECT d.device_id, d.device_name, SUM(bd.quantity) AS total_borrowed
            FROM borrow_details bd
            JOIN devices d ON bd.device_id = d.device_id
            GROUP BY d.device_id
            ORDER BY total_borrowed DESC
            LIMIT 5
            """
        )
        # Giữ nguyên cấu trúc Dictionary thô để tránh lỗi không đồng bộ dữ liệu tại View con
        stats['most_borrowed'] = [dict(row) for row in most_borrowed] if most_borrowed else []

        top_users = self.db.execute_query(
            """
            SELECT u.user_id, u.full_name, COUNT(br.record_id) AS borrow_count
            FROM borrow_records br
            JOIN users u ON br.user_id = u.user_id
            GROUP BY u.user_id
            ORDER BY borrow_count DESC
            LIMIT 5
            """
        )
        stats['top_users'] = [dict(row) for row in top_users] if top_users else []

        overdue_details = self.db.execute_query(
            """
            SELECT br.record_id, u.full_name, d.device_name, bd.quantity, br.expected_return_date
            FROM borrow_records br
            JOIN users u ON br.user_id = u.user_id
            JOIN borrow_details bd ON bd.record_id = br.record_id
            JOIN devices d ON bd.device_id = d.device_id
            WHERE br.status = 'Quá hạn' AND bd.returned = 0
            ORDER BY br.expected_return_date ASC
            LIMIT 5
            """
        )
        stats['overdue_details'] = [dict(row) for row in overdue_details] if overdue_details else []
        return stats

    def get_borrow_history(self):
        history = self.db.execute_query(
            """
            SELECT br.record_id, u.full_name, d.device_name, bd.quantity,
                   br.borrow_date, br.expected_return_date, br.actual_return_date, br.status
            FROM borrow_records br
            JOIN users u ON br.user_id = u.user_id
            JOIN borrow_details bd ON bd.record_id = br.record_id
            JOIN devices d ON bd.device_id = d.device_id
            ORDER BY br.borrow_date DESC
            """
        )
        return [dict(row) for row in history] if history else []