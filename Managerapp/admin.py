from flask import request, jsonify
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from flask_login import current_user
from sqlalchemy import func, extract
import hashlib
from datetime import datetime

# Import app và db từ package chính
from Managerapp import app, db
# Import các Models
from Managerapp.models import NguoiDung, ThamSoQuyDinh, LinhKien, PhieuTiepNhan, PhieuSuaChua, HoaDon, Xe, \
    ChiTietPhieuSuaChua
# Import hàm kiểm tra quyền hạn
from Managerapp.decorators import check_access


# ---------------------------------------------------------
# A. DASHBOARD VIEW (XỬ LÝ THỐNG KÊ)
# ---------------------------------------------------------
class DashboardView(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin/index.html')

    @expose('/get-stats')
    def get_stats(self):
        # 1. Lấy tham số từ Frontend
        stat_type = request.args.get('type')  # revenue / issues / cars
        time_mode = request.args.get('time_mode')  # 'month' hoặc 'year_range'

        labels, data, title = [], [], ""

        # =================================================================
        # TRƯỜNG HỢP A: THỐNG KÊ THEO KHOẢNG NĂM (CHỈ ÁP DỤNG CHO DOANH THU)
        # =================================================================
        if time_mode == 'year_range':
            # Chỉ cho phép thống kê Doanh thu theo năm
            if stat_type != 'revenue':
                return jsonify({'error': 'Chế độ so sánh năm chỉ áp dụng cho Doanh Thu'}), 400

            try:
                start_year = int(request.args.get('start_year'))
                end_year = int(request.args.get('end_year'))
            except (TypeError, ValueError):
                return jsonify({'error': 'Năm không hợp lệ'}), 400

            if start_year > end_year:
                return jsonify({'error': 'Năm bắt đầu phải nhỏ hơn năm kết thúc'}), 400

            # --- TÍNH TỔNG DOANH THU QUA CÁC NĂM ---
            title = f"Tổng Doanh Thu Từ Năm {start_year} - {end_year}"
            results = db.session.query(
                extract('year', HoaDon.ngay_thu_tien).label('year'),
                func.sum(HoaDon.thanh_toan).label('total')
            ).filter(
                extract('year', HoaDon.ngay_thu_tien) >= start_year,
                extract('year', HoaDon.ngay_thu_tien) <= end_year
            ).group_by(extract('year', HoaDon.ngay_thu_tien)).order_by('year').all()

            # Map dữ liệu để đảm bảo các năm không có doanh thu vẫn hiện số 0
            stats = {int(r.year): r.total for r in results}
            for y in range(start_year, end_year + 1):
                labels.append(f"Năm {y}")
                data.append(stats.get(y, 0))

        # =================================================================
        # TRƯỜNG HỢP B: THỐNG KÊ THEO THÁNG (ÁP DỤNG CHO TẤT CẢ)
        # =================================================================
        else:  # time_mode == 'month' hoặc mặc định
            month_str = request.args.get('month')
            if not month_str:
                return jsonify({'error': 'Vui lòng chọn tháng'}), 400

            try:
                year, month = map(int, month_str.split('-'))
            except ValueError:
                return jsonify({'error': 'Lỗi định dạng tháng'}), 400

            # --- 1. DOANH THU THEO NGÀY ---
            if stat_type == 'revenue':
                title = f"Doanh thu chi tiết tháng {month}/{year}"
                results = db.session.query(
                    extract('day', HoaDon.ngay_thu_tien).label('day'),
                    func.sum(HoaDon.thanh_toan).label('total')
                ).filter(
                    extract('year', HoaDon.ngay_thu_tien) == year,
                    extract('month', HoaDon.ngay_thu_tien) == month
                ).group_by('day').all()

                stats = {int(r.day): r.total for r in results}
                import calendar
                days_in_month = calendar.monthrange(year, month)[1]
                for day in range(1, days_in_month + 1):
                    labels.append(f"Ngày {day}")
                    data.append(stats.get(day, 0))

            # --- 2. TOP HẠNG MỤC SỬA CHỮA (VẤN ĐỀ THƯỜNG GẶP) ---
            elif stat_type == 'issues':
                title = f"Top hạng mục sửa chữa tháng {month}/{year}"
                results = db.session.query(
                    ChiTietPhieuSuaChua.hang_muc_sua_chua,
                    func.count(ChiTietPhieuSuaChua.id).label('count')
                ).join(PhieuSuaChua).filter(
                    extract('year', PhieuSuaChua.ngay_lap) == year,
                    extract('month', PhieuSuaChua.ngay_lap) == month
                ).group_by(ChiTietPhieuSuaChua.hang_muc_sua_chua).order_by(
                    func.count(ChiTietPhieuSuaChua.id).desc()).limit(10).all()

                for r in results:
                    labels.append(r.hang_muc_sua_chua)
                    data.append(r.count)

            # --- 3. TỈ LỆ CÁC DÒNG XE ---
            elif stat_type == 'cars':
                title = f"Tỉ lệ các dòng xe tháng {month}/{year}"
                col = Xe.loai_xe
                results = db.session.query(
                    col, func.count(PhieuTiepNhan.id).label('count')
                ).join(PhieuTiepNhan, Xe.id == PhieuTiepNhan.ma_xe).filter(
                    extract('year', PhieuTiepNhan.ngay_tiep_nhan) == year,
                    extract('month', PhieuTiepNhan.ngay_tiep_nhan) == month
                ).group_by(col).all()

                for r in results:
                    labels.append(r[0] if r[0] else "Khác")
                    data.append(r.count)

        return jsonify({'labels': labels, 'data': data, 'title': title})

    def is_accessible(self):
        # Chỉ cho phép Admin và Quản lý truy cập
        return check_access(['Admin', 'QuanLy'])


# ---------------------------------------------------------
# B. CÁC VIEW QUẢN LÝ MODEL (CRUD)
# ---------------------------------------------------------
class UserView(ModelView):
    """View quản lý người dùng - Có mã hóa mật khẩu"""
    column_list = ('ho_ten', 'tai_khoan', 'user_role', 'active')
    form_columns = ('ho_ten', 'tai_khoan', 'mat_khau', 'role_info', 'active')

    column_labels = {
        'ho_ten': 'Họ tên', 'tai_khoan': 'Tài khoản',
        'mat_khau': 'Mật khẩu', 'user_role': 'Vai trò',
        'active': 'Kích hoạt', 'role_info': 'Phân quyền'
    }

    def on_model_change(self, form, model, is_created):
        # Nếu có nhập mật khẩu thì mã hóa MD5
        if form.mat_khau.data:
            model.mat_khau = str(hashlib.md5(form.mat_khau.data.strip().encode("utf-8")).hexdigest())

    def is_accessible(self):
        return check_access(['Admin'])


class BaseRoleView(ModelView):
    """View cơ bản cho các bảng khác"""

    def is_accessible(self):
        return check_access(['Admin', 'QuanLy'])


# ---------------------------------------------------------
# C. KHỞI TẠO ADMIN
# ---------------------------------------------------------

admin = Admin(app, name='GARA ADMIN', index_view=DashboardView())

admin.add_view(UserView(NguoiDung, db.session, name='Tài Khoản'))
admin.add_view(BaseRoleView(ThamSoQuyDinh, db.session, name='Quy Định'))
admin.add_view(BaseRoleView(LinhKien, db.session, name='Kho Linh Kiện'))
admin.add_view(BaseRoleView(PhieuTiepNhan, db.session, name='Phiếu Tiếp Nhận'))
admin.add_view(BaseRoleView(PhieuSuaChua, db.session, name='Phiếu Sửa Chữa'))
admin.add_view(BaseRoleView(HoaDon, db.session, name='Hoá Đơn'))

admin.add_link(MenuLink(name='Tạo tài khoản', endpoint='admin_create_account'))
admin.add_link(MenuLink(name='Đăng xuất', endpoint='logout_process'))