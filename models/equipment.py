"""Model Equipment - Đại diện cho thiết bị/lệnh kiện."""

class Equipment:
    """Lớp đại diện cho thiết bị hoặc linh kiện trong hệ thống."""

    VALID_STATUSES = ['Có sẵn', 'Đang được mượn', 'Đang bảo trì']

    def __init__(
        self,
        equipment_id="",
        equipment_name="",
        category="",
        total_quantity=0,
        available_quantity=0,
        status='Có sẵn',
    ):
        self._equipment_id = equipment_id
        self._equipment_name = equipment_name
        self._category = category
        self._total_quantity = total_quantity
        self._available_quantity = available_quantity
        self._status = status

    @property
    def equipment_id(self):
        return self._equipment_id

    @equipment_id.setter
    def equipment_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã thiết bị không được để trống")
        self._equipment_id = value.strip()

    @property
    def equipment_name(self):
        return self._equipment_name

    @equipment_name.setter
    def equipment_name(self, value):
        if not value or not value.strip():
            raise ValueError("Tên thiết bị không được để trống")
        self._equipment_name = value.strip()

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        if not value or not value.strip():
            raise ValueError("Phân loại không được để trống")
        self._category = value.strip()

    @property
    def total_quantity(self):
        return self._total_quantity

    @total_quantity.setter
    def total_quantity(self, value):
        if int(value) < 0:
            raise ValueError("Số lượng tổng không được âm")
        if int(value) < self._available_quantity:
            raise ValueError("Số lượng tổng không thể nhỏ hơn số lượng khả dụng")
        self._total_quantity = int(value)

    @property
    def available_quantity(self):
        return self._available_quantity

    @available_quantity.setter
    def available_quantity(self, value):
        if int(value) < 0:
            raise ValueError("Số lượng khả dụng không được âm")
        if int(value) > self._total_quantity:
            raise ValueError("Số lượng khả dụng không thể lớn hơn số lượng tổng")
        self._available_quantity = int(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Trạng thái phải là một trong: {', '.join(self.VALID_STATUSES)}")
        self._status = value

    def to_tuple(self):
        return (
            self._equipment_id,
            self._equipment_name,
            self._category,
            self._total_quantity,
            self._available_quantity,
            self._status,
        )

    def __str__(self):
        return f"Equipment({self._equipment_id}, {self._equipment_name}, {self._status})"

    def __repr__(self):
        return self.__str__()
