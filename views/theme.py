"""
Bộ quản lý Theme hỗ trợ Light Mode và Dark Mode chuẩn Minimalist.
"""

def get_stylesheet(is_dark=False):
    # Hệ màu Tối giản (Minimalist)
    if is_dark:
        bg_main = "#0f172a"          # Nền chính (Slate 900)
        bg_surface = "#1e293b"       # Nền khối (Slate 800)
        bg_input = "#0f172a"         # Nền ô nhập liệu
        border_color = "#334155"     # Viền (Slate 700)
        text_primary = "#f8fafc"     # Chữ chính (Slate 50)
        text_secondary = "#94a3b8"   # Chữ phụ (Slate 400)
        accent_color = "#3b82f6"     # Accent Blue
        hover_bg = "#2563eb"         # Hover Blue
        table_alt = "#1e293b"        # Nền bảng xen kẽ
        table_bg = "#0f172a"         # Nền bảng
    else:
        bg_main = "#f8fafc"          # Nền chính (Slate 50)
        bg_surface = "#ffffff"       # Nền khối trắng
        bg_input = "#ffffff"         # Nền ô nhập liệu
        border_color = "#e2e8f0"     # Viền (Slate 200)
        text_primary = "#0f172a"     # Chữ chính (Slate 900)
        text_secondary = "#64748b"   # Chữ phụ (Slate 500)
        accent_color = "#2563eb"     # Accent Blue
        hover_bg = "#1d4ed8"         # Hover Blue
        table_alt = "#f8fafc"        # Nền bảng xen kẽ
        table_bg = "#ffffff"         # Nền bảng

    return f"""
    /* --- CẤU HÌNH CHUNG --- */
    QMainWindow, QDialog, QWidget {{
        background-color: {bg_main};
        color: {text_primary};
        font-family: "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;
        font-size: 13px;
    }}

    /* Loại trừ QWidget bên trong các container để tránh đè nền */
    QGroupBox QWidget, QTabWidget QWidget {{
        background-color: transparent;
    }}

    /* --- TIÊU ĐỀ KHỐI (GROUP BOX) --- */
    QGroupBox {{
        background-color: {bg_surface};
        border: 1px solid {border_color};
        border-radius: 8px;
        margin-top: 20px;
        padding-top: 15px;
    }}
    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 10px;
        left: 15px;
        color: {accent_color};
        font-weight: bold;
    }}

    /* --- Ô NHẬP LIỆU (LINE EDIT, SPIN BOX, COMBO BOX) --- */
    QLineEdit, QSpinBox, QComboBox, QDateEdit {{
        background-color: {bg_input};
        border: 1px solid {border_color};
        border-radius: 6px;
        padding: 8px 12px;
        color: {text_primary};
        min-height: 20px;
    }}
    QLineEdit:focus, QSpinBox:focus, QComboBox:focus, QDateEdit:focus {{
        border: 1px solid {accent_color};
        background-color: {bg_surface};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 30px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {bg_surface};
        border: 1px solid {border_color};
        selection-background-color: {accent_color};
        selection-color: #ffffff;
    }}

    /* --- NÚT BẤM CHUNG (PUSH BUTTON) --- */
    QPushButton {{
        background-color: {bg_surface};
        border: 1px solid {border_color};
        border-radius: 6px;
        color: {text_primary};
        padding: 8px 16px;
        font-weight: 500;
        min-height: 20px;
    }}
    QPushButton:hover {{
        background-color: {border_color};
    }}
    QPushButton:pressed {{
        background-color: {text_secondary};
    }}

    /* --- TAB WIDGET (THANH ĐIỀU HƯỚNG MÀN HÌNH) --- */
    QTabWidget::pane {{
        border: 1px solid {border_color};
        border-radius: 8px;
        background-color: {bg_surface};
        top: -1px;
    }}
    QTabBar::tab {{
        background-color: transparent;
        color: {text_secondary};
        padding: 10px 20px;
        border-bottom: 2px solid transparent;
        font-weight: bold;
        font-size: 14px;
        margin-right: 5px;
    }}
    QTabBar::tab:hover {{
        color: {accent_color};
    }}
    QTabBar::tab:selected {{
        color: {accent_color};
        border-bottom: 2px solid {accent_color};
    }}

    /* --- BẢNG DỮ LIỆU (TABLE WIDGET) --- */
    QTableWidget {{
        background-color: {table_bg};
        alternate-background-color: {table_alt};
        border: 1px solid {border_color};
        border-radius: 8px;
        color: {text_primary};
        gridline-color: {border_color};
        selection-background-color: {accent_color};
        selection-color: #ffffff;
    }}
    QHeaderView::section {{
        background-color: {bg_surface};
        color: {text_secondary};
        padding: 10px;
        border: none;
        border-bottom: 1px solid {border_color};
        border-right: 1px solid {border_color};
        font-weight: bold;
    }}
    QTableWidget::item {{
        padding: 5px;
        border-bottom: 1px solid {border_color};
    }}
    
    /* --- THANH CUỘN (SCROLLBAR) --- */
    QScrollBar:vertical {{
        border: none;
        background: transparent;
        width: 10px;
        margin: 0px 0px 0px 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {border_color};
        min-height: 20px;
        border-radius: 5px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: {text_secondary};
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """

def get_button_style(btn_type="primary", is_dark=False) -> str:
    """
    Sử dụng cho các nút bấm chỉ định trực tiếp (Nút Xác nhận, Cảnh báo).
    Ghi đè lên style chung của QPushButton.
    """
    if btn_type == "primary":
        bg_color = "#2563eb" # Xanh Blue
        hover_color = "#1d4ed8"
        text_color = "#ffffff"
    elif btn_type == "success":
        bg_color = "#16a34a" # Xanh Green
        hover_color = "#15803d"
        text_color = "#ffffff"
    elif btn_type == "danger":
        bg_color = "#dc2626" # Đỏ
        hover_color = "#b91c1c"
        text_color = "#ffffff"
    else: # Secondary
        bg_color = "#334155" if is_dark else "#e2e8f0"
        hover_color = "#475569" if is_dark else "#cbd5e1"
        text_color = "#f8fafc" if is_dark else "#0f172a"

    return f"""
        QPushButton {{
            background-color: {bg_color};
            color: {text_color};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """