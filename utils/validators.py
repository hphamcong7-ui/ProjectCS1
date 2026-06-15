"""Các hàm tiện ích để kiểm tra dữ liệu đầu vào."""

import re


def is_empty(value):
    """Kiểm tra giá trị có rỗng không."""
    return value is None or str(value).strip() == ""


def is_positive_integer(value):
    """Kiểm tra giá trị có phải số nguyên dương không."""
    try:
        num = int(value)
        return num >= 0
    except (ValueError, TypeError):
        return False


def is_valid_email(email):
    if is_empty(email):
        return False
    pattern = r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def validate_equipment_input(equipment_id, name, category, total_qty, available_qty, status=None):
    if is_empty(equipment_id):
        return False, "Mã thiết bị không được để trống!"
    if is_empty(name):
        return False, "Tên thiết bị không được để trống!"
    if is_empty(category):
        return False, "Phân loại không được để trống!"
    if not is_positive_integer(total_qty):
        return False, "Số lượng tổng phải là số nguyên không âm!"
    if not is_positive_integer(available_qty):
        return False, "Số lượng khả dụng phải là số nguyên không âm!"
    if int(available_qty) > int(total_qty):
        return False, "Số lượng khả dụng không thể lớn hơn số lượng tổng!"
    return True, ""


def validate_user_input(user_id, full_name, email, role, password=None, confirm_password=None):
    if is_empty(user_id):
        return False, "Mã người dùng không được để trống!"
    if is_empty(full_name):
        return False, "Họ tên không được để trống!"
    if is_empty(email) or not is_valid_email(email):
        return False, "Email không hợp lệ!"
    if is_empty(role):
        return False, "Vai trò không được để trống!"
    if password is not None:
        if len(password) < 6:
            return False, "Mật khẩu phải có ít nhất 6 ký tự!"
        if password != confirm_password:
            return False, "Mật khẩu và xác nhận mật khẩu không khớp!"
    return True, ""


def validate_borrow_cart(user_id, borrowed_items, expected_date):
    if is_empty(user_id):
        return False, "Vui lòng chọn người mượn!"
    if not borrowed_items:
        return False, "Vui lòng thêm ít nhất một thiết bị vào giỏ mượn!"
    if expected_date is None:
        return False, "Vui lòng chọn ngày trả dự kiến!"
    return True, ""
