from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


# -----------------------------------------------------------
# HÀM HỖ TRỢ: Trả về True/False (Dùng cho cả Admin & Decorator)
# -----------------------------------------------------------
def check_access(allowed_roles):
    """
    Hàm này chỉ trả về True/False, không Redirect.
    Dùng để check trong is_accessible của Flask-Admin.
    """
    if not current_user.is_authenticated:
        return False
    # So sánh chính xác (phân biệt hoa thường)
    return current_user.user_role in allowed_roles


# -----------------------------------------------------------
# DECORATORS (Dùng cho Routes trong app.py)
# -----------------------------------------------------------

# 1. CHẶN NGƯỜI DÙNG ĐÃ ĐĂNG NHẬP (Dùng cho trang Login/Register)
def anonymous_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index'))
        return f(*args, **kwargs)

    return decorated_function


# 2. HÀM GỐC: KIỂM TRA ROLE VÀ REDIRECT
def check_role(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # [SỬA LỖI] Sử dụng hàm check_access ở trên
            if not check_access(allowed_roles):
                # Nếu chưa đăng nhập -> Login
                if not current_user.is_authenticated:
                    return redirect(url_for('login_user_view'))

                # Nếu đã đăng nhập nhưng sai quyền -> Báo lỗi 403 hoặc về trang chủ
                flash("Bạn không có quyền truy cập trang này!", "danger")
                return redirect(url_for('index'))

            return f(*args, **kwargs)

        return decorated_function

    return decorator


# --- CÁC DECORATOR CỤ THỂ ---

# A. Nhóm Quản Trị (Admin + Quản lý)
def admin_manager_required(f):
    return check_role(['Admin', 'QuanLy'])(f)


# B. Nhóm Nghiệp vụ Tiếp Nhận (Admin + Quản lý + Nhân viên)
def sales_task_required(f):
    return check_role(['Admin', 'QuanLy', 'NhanVien'])(f)


# C. Nhóm Nghiệp vụ Sửa Chữa (Admin + Quản lý + Kỹ thuật viên)
def tech_task_required(f):
    return check_role(['Admin', 'QuanLy', 'KyThuatVien'])(f)