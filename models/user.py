"""Model User - Đại diện cho người dùng hệ thống."""

from datetime import datetime


class User:
    """Lớp đại diện cho người dùng hệ thống."""

    VALID_ROLES = ['Admin', 'User', 'admin', 'user']

    def __init__(
        self,
        user_id="",
        full_name="",
        email="",
        phone="",
        password_hash="",
        role="User",
        created_at=None,
        is_active=True,
    ):
        self._user_id = user_id
        self._full_name = full_name
        self._email = email
        self._phone = phone
        self._password_hash = password_hash
        self._role = role
        self._created_at = created_at or datetime.utcnow()
        self._is_active = bool(is_active)

    @property
    def user_id(self):
        return self._user_id

    @user_id.setter
    def user_id(self, value):
        if not value or not value.strip():
            raise ValueError("Mã người dùng không được để trống")
        self._user_id = value.strip()

    @property
    def full_name(self):
        return self._full_name

    @full_name.setter
    def full_name(self, value):
        if not value or not value.strip():
            raise ValueError("Họ tên không được để trống")
        self._full_name = value.strip()

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, value):
        if not value or not value.strip():
            raise ValueError("Email không được để trống")
        self._email = value.strip().lower()

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, value):
        self._phone = value.strip() if value else ""

    @property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, value):
        self._password_hash = value

    @property
    def role(self):
        return self._role
    
    @role.setter
    def role(self, value):
        if not value:
            self._role = 'User'
            return
        normalized_role = str(value).strip().capitalize()
        if normalized_role not in self.VALID_ROLES:
            raise ValueError(f"Role invalid. Accepted values: {', '.join(self.VALID_ROLES)}")
        self._role = normalized_role

    @property
    def created_at(self):
        return self._created_at

    @property
    def is_active(self):
        return self._is_active

    def to_tuple(self):
        return (
            self._user_id,
            self._full_name,
            self._email,
            self._phone,
            self._role,
        )

    def __str__(self):
        return f"User({self._user_id}, {self._full_name}, {self._email}, {self._role})"
