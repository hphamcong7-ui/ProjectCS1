"""Model BorrowDetail - Đại diện cho chi tiết thiết bị trong phiếu mượn."""

from datetime import datetime


class BorrowDetail:
    """Lưu trữ chi tiết thiết bị mượn trong phiếu."""

    def __init__(
        self,
        detail_id=None,
        record_id="",
        device_id="",
        device_name="",
        quantity=0,
        returned=0,
        return_date=None,
        condition_on_return="",
    ):
        self.detail_id = detail_id
        self.record_id = record_id
        self.device_id = device_id
        self.device_name = device_name
        self.quantity = quantity
        self.returned = bool(returned)
        self.return_date = return_date
        self.condition_on_return = condition_on_return

    @property
    def detail_id(self):
        return self._detail_id

    @detail_id.setter
    def detail_id(self, value):
        self._detail_id = value

    @property
    def record_id(self):
        return self._record_id

    @record_id.setter
    def record_id(self, value):
        self._record_id = value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã thiết bị không được để trống")
        self._device_id = value.strip()

    @property
    def device_name(self):
        return self._device_name

    @device_name.setter
    def device_name(self, value):
        self._device_name = value.strip() if value else ''

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if int(value) <= 0:
            raise ValueError("Số lượng mượn phải lớn hơn 0")
        self._quantity = int(value)

    @property
    def returned(self):
        return self._returned

    @returned.setter
    def returned(self, value):
        self._returned = bool(value)

    @property
    def return_date(self):
        return self._return_date

    @return_date.setter
    def return_date(self, value):
        self._return_date = value

    @property
    def condition_on_return(self):
        return self._condition_on_return

    @condition_on_return.setter
    def condition_on_return(self, value):
        self._condition_on_return = value.strip() if value else ''

    def to_tuple(self):
        return (
            self.detail_id,
            self.device_id,
            self.device_name,
            self.quantity,
            'Đã trả' if self.returned else 'Chưa trả',
            self.return_date.strftime('%d/%m/%Y') if self.return_date else '',
            self.condition_on_return,
        )
