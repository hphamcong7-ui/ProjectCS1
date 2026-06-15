"""Model BorrowRecord - Đại diện cho phiếu mượn."""

from datetime import datetime


class BorrowRecord:
    """Lưu trữ thông tin phiếu mượn và trạng thái chung."""

    VALID_STATUSES = ['Chờ phê duyệt', 'Đã phê duyệt', 'Đang mượn', 'Đã trả', 'Quá hạn']

    def __init__(
        self,
        record_id="",
        user_id="",
        borrow_date=None,
        expected_return_date=None,
        actual_return_date=None,
        status='Đang mượn',
        notes='',
        details=None,
    ):
        self.record_id = record_id
        self.user_id = user_id
        self.borrow_date = borrow_date or datetime.utcnow()
        self.expected_return_date = expected_return_date
        self.actual_return_date = actual_return_date
        self.status = status
        self.notes = notes
        self.details = details or []

    @property
    def record_id(self):
        return self._record_id

    @record_id.setter
    def record_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã phiếu mượn không được để trống")
        self._record_id = value.strip()

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã người mượn không được để trống")
        self._user_id = value.strip()

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
        if value and value < self.borrow_date:
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
        if value not in self.VALID_STATUSES:
            raise ValueError(f"Trạng thái phải là một trong: {', '.join(self.VALID_STATUSES)}")
        self._status = value

    @property
    def notes(self):
        return self._notes

    @notes.setter
    def notes(self, value):
        self._notes = value.strip() if value else ''

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value or []

    def to_summary_tuple(self):
        borrow_date = self.borrow_date.strftime("%d/%m/%Y") if self.borrow_date else ""
        expected_date = self.expected_return_date.strftime("%d/%m/%Y") if self.expected_return_date else ""
        actual_date = self.actual_return_date.strftime("%d/%m/%Y") if self.actual_return_date else ""
        return (
            self.record_id,
            self.user_id,
            borrow_date,
            expected_date,
            actual_date,
            self.status,
        )
