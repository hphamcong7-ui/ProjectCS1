"""
Model BorrowTransaction - Đại diện cho Phiếu mượn
"""

from datetime import datetime

class BorrowTransaction:
    """
    Lớp đại diện cho một giao dịch mượn thiết bị.
    
    Attributes:
        transaction_id (str): Mã phiếu mượn
        user_id (str): Mã người mượn
        equipment_id (str): Mã thiết bị
        borrow_quantity (int): Số lượng mượn
        borrow_date (datetime): Ngày mượn
        expected_return_date (datetime): Ngày dự kiến trả
        actual_return_date (datetime): Ngày trả thực tế (None nếu chưa trả)
        status (str): Trạng thái (Đang mượn, Đã trả, Quá hạn)
    """
    
    VALID_STATUS = ['Đang mượn', 'Đã trả', 'Quá hạn']
    
    def __init__(self, transaction_id="", user_id="", equipment_id="",
                 borrow_quantity=0, borrow_date=None, expected_return_date=None,
                 actual_return_date=None, status="Đang mượn"):
        self._transaction_id = transaction_id
        self._user_id = user_id
        self._equipment_id = equipment_id
        self._borrow_quantity = borrow_quantity
        self._borrow_date = borrow_date or datetime.now()
        self._expected_return_date = expected_return_date
        self._actual_return_date = actual_return_date
        self._status = status
    
    @property
    def transaction_id(self):
        return self._transaction_id
    
    @transaction_id.setter
    def transaction_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã phiếu mượn không được để trống")
        self._transaction_id = value.strip()
    
    @property
    def user_id(self):
        return self._user_id
    
    @user_id.setter
    def user_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã người mượn không được để trống")
        self._user_id = value.strip()
    
    @property
    def equipment_id(self):
        return self._equipment_id
    
    @equipment_id.setter
    def equipment_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã thiết bị không được để trống")
        self._equipment_id = value.strip()
    
    @property
    def borrow_quantity(self):
        return self._borrow_quantity
    
    @borrow_quantity.setter
    def borrow_quantity(self, value):
        if value <= 0:
            raise ValueError("Số lượng mượn phải lớn hơn 0")
        self._borrow_quantity = value
    
    @property
    def borrow_date(self):
        return self._borrow_date
    
    @borrow_date.setter
    def borrow_date(self, value):
        self._borrow_date = value
    
    @property
    def expected_return_date(self):
        return self._expected_return_date
    
    @expected_return_date.setter
    def expected_return_date(self, value):
        if value and value < self._borrow_date:
            raise ValueError("Ngày trả dự kiến phải sau ngày mượn")
        self._expected_return_date = value
    
    @property
    def actual_return_date(self):
        return self._actual_return_date
    
    @actual_return_date.setter
    def actual_return_date(self, value):
        self._actual_return_date = value
    
    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        if value not in self.VALID_STATUS:
            raise ValueError(f"Trạng thái phải là: {', '.join(self.VALID_STATUS)}")
        self._status = value
    
    def to_tuple(self):
        """Chuyển đổi object thành tuple để hiển thị"""
        return (
            self._transaction_id,
            self._user_id,
            self._equipment_id,
            self._borrow_quantity,
            self._borrow_date.strftime("%d/%m/%Y") if self._borrow_date else "",
            self._expected_return_date.strftime("%d/%m/%Y") if self._expected_return_date else "",
            self._actual_return_date.strftime("%d/%m/%Y") if self._actual_return_date else "",
            self._status
        )
