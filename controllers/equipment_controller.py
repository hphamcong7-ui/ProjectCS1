"""Controller xử lý các thao tác CRUD cho thiết bị."""

from controllers.database_connection import DatabaseConnection
from models.equipment import Equipment


class EquipmentController:
    """Lớp điều khiển xử lý logic nghiệp vụ cho thiết bị."""

    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_equipments(self):
        query = """
            SELECT device_id, device_name, category, total_quantity,
                   available_quantity, status
            FROM devices
            ORDER BY device_id
        """
        try:
            results = self.db.execute_query(query)
            equipments = []
            for row in results:
                equipments.append(
                    Equipment(
                        equipment_id=row['device_id'],
                        equipment_name=row['device_name'],
                        category=row['category'],
                        total_quantity=row['total_quantity'],
                        available_quantity=row['available_quantity'],
                        status=row['status'],
                    )
                )
            return equipments
        except Exception as e:
            raise Exception(f"Lỗi lấy danh sách thiết bị: {str(e)}")

    def get_equipment_by_id(self, equipment_id):
        query = """
            SELECT device_id, device_name, category, total_quantity,
                   available_quantity, status
            FROM devices
            WHERE device_id = ?
        """
        try:
            results = self.db.execute_query(query, (equipment_id,))
            if results:
                row = results[0]
                return Equipment(
                    equipment_id=row['device_id'],
                    equipment_name=row['device_name'],
                    category=row['category'],
                    total_quantity=row['total_quantity'],
                    available_quantity=row['available_quantity'],
                    status=row['status'],
                )
            return None
        except Exception as e:
            raise Exception(f"Lỗi tìm thiết bị: {str(e)}")

    def search_equipments(self, keyword):
        query = """
            SELECT device_id, device_name, category, total_quantity,
                   available_quantity, status
            FROM devices
            WHERE device_id LIKE ? OR device_name LIKE ? OR category LIKE ?
            ORDER BY device_id
        """
        search_pattern = f"%{keyword}%"
        try:
            results = self.db.execute_query(
                query,
                (search_pattern, search_pattern, search_pattern),
            )
            equipments = []
            for row in results:
                equipments.append(
                    Equipment(
                        equipment_id=row['device_id'],
                        equipment_name=row['device_name'],
                        category=row['category'],
                        total_quantity=row['total_quantity'],
                        available_quantity=row['available_quantity'],
                        status=row['status'],
                    )
                )
            return equipments
        except Exception as e:
            raise Exception(f"Lỗi tìm kiếm thiết bị: {str(e)}")

    def add_equipment(self, equipment):
        if self.get_equipment_by_id(equipment.equipment_id):
            raise Exception(f"Mã thiết bị '{equipment.equipment_id}' đã tồn tại.")

        status = equipment.status
        if equipment.available_quantity == 0 and equipment.total_quantity > 0:
            status = 'Đang được mượn'

        query = """
            INSERT INTO devices
            (device_id, device_name, category, total_quantity, available_quantity, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            equipment.equipment_id,
            equipment.equipment_name,
            equipment.category,
            equipment.total_quantity,
            equipment.available_quantity,
            status,
        )
        try:
            self.db.execute_non_query(query, params)
            return True
        except Exception as e:
            raise Exception(f"Lỗi thêm thiết bị: {str(e)}")

    def update_equipment(self, equipment):
        if equipment.available_quantity < 0 or equipment.total_quantity < 0:
            raise ValueError("Số lượng không hợp lệ.")

        status = equipment.status
        if equipment.available_quantity == 0 and equipment.total_quantity > 0:
            status = 'Đang được mượn'
        elif equipment.available_quantity > 0 and status == 'Đang được mượn':
            status = 'Có sẵn'

        query = """
            UPDATE devices
            SET device_name = ?, category = ?, total_quantity = ?,
                available_quantity = ?, status = ?
            WHERE device_id = ?
        """
        params = (
            equipment.equipment_name,
            equipment.category,
            equipment.total_quantity,
            equipment.available_quantity,
            status,
            equipment.equipment_id,
        )
        try:
            rows_affected = self.db.execute_non_query(query, params)
            if rows_affected == 0:
                raise Exception(f"Không tìm thấy thiết bị có mã '{equipment.equipment_id}'")
            return True
        except Exception as e:
            raise Exception(f"Lỗi cập nhật thiết bị: {str(e)}")

    def delete_equipment(self, equipment_id):
        check_query = """
            SELECT COUNT(*) AS cnt
            FROM borrow_details bd
            JOIN borrow_records br ON bd.record_id = br.record_id
            WHERE bd.device_id = ? AND bd.returned = 0
        """
        try:
            result = self.db.execute_query(check_query, (equipment_id,))
            if result and result[0]['cnt'] > 0:
                raise Exception("Không thể xóa! Thiết bị đang được mượn.")

            rows_affected = self.db.execute_non_query(
                "DELETE FROM devices WHERE device_id = ?", (equipment_id,)
            )
            if rows_affected == 0:
                raise Exception(f"Không tìm thấy thiết bị có mã '{equipment_id}'")
            return True
        except Exception as e:
            raise Exception(f"Lỗi xóa thiết bị: {str(e)}")

    def get_categories(self):
        query = "SELECT DISTINCT category FROM devices ORDER BY category"
        try:
            results = self.db.execute_query(query)
            return [row['category'] for row in results]
        except Exception as e:
            raise Exception(f"Lỗi lấy danh sách phân loại: {str(e)}")

    def update_status_if_needed(self, equipment_id):
        equipment = self.get_equipment_by_id(equipment_id)
        if not equipment:
            return
        if equipment.available_quantity == 0 and equipment.total_quantity > 0:
            status = 'Đang được mượn'
        elif equipment.status == 'Đang được mượn' and equipment.available_quantity > 0:
            status = 'Có sẵn'
        else:
            status = equipment.status
        self.db.execute_non_query(
            "UPDATE devices SET status = ? WHERE device_id = ?",
            (status, equipment_id),
        )
