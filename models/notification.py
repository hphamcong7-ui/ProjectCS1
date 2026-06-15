"""Model Notification - Đại diện cho thông báo hệ thống."""

from datetime import datetime


class Notification:
    """Lưu trữ dữ liệu thông báo."""

    def __init__(
        self,
        notification_id=None,
        user_id=None,
        title="",
        message="",
        created_at=None,
        is_read=False,
        type_="info",
    ):
        self.notification_id = notification_id
        self.user_id = user_id
        self.title = title
        self.message = message
        self.created_at = created_at or datetime.utcnow()
        self.is_read = bool(is_read)
        self.type = type_

    @property
    def notification_id(self):
        return self._notification_id

    @notification_id.setter
    def notification_id(self, value):
        self._notification_id = value

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        self._user_id = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value.strip() if value else ''

    @property
    def message(self):
        return self._message

    @message.setter
    def message(self, value):
        self._message = value.strip() if value else ''

    @property
    def created_at(self):
        return self._created_at

    @created_at.setter
    def created_at(self, value):
        self._created_at = value

    @property
    def is_read(self):
        return self._is_read

    @is_read.setter
    def is_read(self, value):
        self._is_read = bool(value)

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value.strip() if value else 'info'

    def to_tuple(self):
        created = self.created_at.strftime('%d/%m/%Y %H:%M') if self.created_at else ''
        return (
            self.notification_id,
            self.user_id or 'Tất cả',
            self.title,
            self.message,
            created,
            'Đã đọc' if self.is_read else 'Chưa đọc',
            self.type,
        )
