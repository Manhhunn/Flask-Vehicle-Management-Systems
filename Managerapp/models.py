import hashlib

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from Managerapp import db, app



class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now)
    updated_date = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Role(BaseModel):
    __tablename__ = 'role'
    role_name = Column(String(50), nullable=False, unique=True)
    role_value = Column(String(50), nullable=True)
    users = relationship('NguoiDung', backref='role_info', lazy=True)

    def __str__(self): return self.role_name


class NguoiDung(BaseModel, UserMixin):
    __tablename__ = 'nguoi_dung'
    ho_ten = Column(String(100), nullable=False)
    tai_khoan = Column(String(50), unique=True, nullable=False)
    mat_khau = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey('role.id'), nullable=False)

    @property
    def user_role(self): return self.role_info.role_value if self.role_info else None

    phieu_tiep_nhans = relationship('PhieuTiepNhan', backref='nguoi_tao', lazy=True)
    phieu_sua_chuas = relationship('PhieuSuaChua', backref='nguoi_tao', lazy=True)
    hoa_dons = relationship('HoaDon', backref='nguoi_tao', lazy=True)

    def __str__(self): return self.ho_ten



class LinhKien(BaseModel):
    __tablename__ = 'linh_kien'
    # Bỏ ma_linh_kien, chỉ dùng ID
    ten_linh_kien = db.Column(db.String(100), nullable=False)
    don_gia_ban = db.Column(db.Float, nullable=False)
    so_luong_ton = db.Column(db.Integer, default=0)
    chi_tiet_sua_chua = db.relationship('ChiTietPhieuSuaChua', backref='linh_kien', lazy=True)


class TienCong(BaseModel):
    __tablename__ = 'tien_cong'
    noi_dung = db.Column(db.String(255), nullable=False)
    tien_cong_ = db.Column(db.Float, nullable=False)
    chi_tiet_sua_chua = db.relationship('ChiTietPhieuSuaChua', backref='tien_cong', lazy=True)


class ThamSoQuyDinh(BaseModel):
    __tablename__ = 'tham_so_quy_dinh'
    ma_quy_dinh = db.Column(db.String(50), unique=True, nullable=False)
    ten_qui_dinh = db.Column(db.String(100), nullable=False, unique=True)
    gia_tri = db.Column(db.String(100), nullable=False)


class Xe(BaseModel):
    __tablename__ = 'xe'
    bien_so = db.Column(db.String(20), unique=True, nullable=False)
    ten_khach_hang = db.Column(db.String(100), nullable=False)
    loai_xe = db.Column(db.String(50))
    tien_no = db.Column(db.Float, default=0.0)
    ds_phieu_tiep_nhan = db.relationship('PhieuTiepNhan', backref='xe', lazy=True)
    ds_hoa_don = db.relationship('HoaDon', backref='xe', lazy=True)


class PhieuTiepNhan(BaseModel):
    __tablename__ = 'phieu_tiep_nhan'
    ngay_tiep_nhan = db.Column(db.DateTime, default=datetime.now)
    loi_mo_ta = db.Column(db.String(255))
    ma_xe = db.Column(db.Integer, db.ForeignKey('xe.id'), nullable=False)
    phieu_sua_chua = db.relationship('PhieuSuaChua', backref='phieu_tiep_nhan', uselist=False, lazy=True)
    nguoi_tao_id = Column(Integer, ForeignKey('nguoi_dung.id'), nullable=False)



class PhieuSuaChua(BaseModel):
    __tablename__ = 'phieu_sua_chua'
    ngay_lap = db.Column(db.DateTime, default=datetime.now)
    tong_thanh_tien = db.Column(db.Float, default=0.0)
    ma_phieu_tiep_nhan = db.Column(db.Integer, db.ForeignKey('phieu_tiep_nhan.id'), unique=True, nullable=False)
    chi_tiet = db.relationship('ChiTietPhieuSuaChua', backref='phieu_sua_chua', lazy=True)
    hoa_don = db.relationship('HoaDon', backref='phieu_sua_chua', lazy=True, uselist=False)
    nguoi_tao_id = Column(Integer, ForeignKey('nguoi_dung.id'), nullable=False)


class ChiTietPhieuSuaChua(BaseModel):
    __tablename__ = 'chi_tiet_phieu_sua_chua'
    hang_muc_sua_chua = db.Column(db.String(255))
    so_luong = db.Column(db.Integer, default=1)
    don_gia_luu_tru = db.Column(db.Float, default=0.0)
    tien_cong_luu_tru = db.Column(db.Float, default=0.0)
    thanh_tien = db.Column(db.Float, default=0.0)
    ma_phieu_sua = db.Column(db.Integer, db.ForeignKey('phieu_sua_chua.id'), nullable=False)

    linh_kien_id = db.Column(db.Integer, db.ForeignKey('linh_kien.id'), nullable=True)
    tien_cong_id = db.Column(db.Integer, db.ForeignKey('tien_cong.id'), nullable=True)


class HoaDon(BaseModel):
    __tablename__ = 'hoa_don'
    ngay_thu_tien = db.Column(db.DateTime, default=datetime.now)
    thanh_toan = db.Column(db.Float, nullable=False)
    ma_xe = db.Column(db.Integer, db.ForeignKey('xe.id'), nullable=False)
    ma_phieu_sua = db.Column(db.Integer, db.ForeignKey('phieu_sua_chua.id'), nullable=True, unique=True)
    nguoi_tao_id = Column(Integer, ForeignKey('nguoi_dung.id'), nullable=False)



# with app.app_context():
#     if __name__ == "__main__":
#         db.create_all()
#
#         if not Role.query.first():
#             # 1. Roles
#             r1 = Role(role_name='Quản trị hệ thống', role_value='Admin')
#             r2 = Role(role_name='Quản lý cửa hàng', role_value='QuanLy')
#             r3 = Role(role_name='Nhân viên', role_value='NhanVien')
#             r4 = Role(role_name='Kỹ thuật viên', role_value='KyThuatVien')
#             db.session.add_all([r1, r2, r3, r4])
#             db.session.commit()
#
#             # 2. Admin
#             pass_hash = str(hashlib.md5("123456".strip().encode("utf-8")).hexdigest())
#             admin = NguoiDung(ho_ten="Admin", tai_khoan="admin", mat_khau=pass_hash, role_id=r1.id)
#             db.session.add(admin)
#
#             # 3. Quy định (Bỏ ma_qui_dinh -> Dùng ten_qui_dinh để tìm kiếm)
#             # LƯU Ý: Tên phải đặt cố định để code dao.py tìm được
#
#             qd1 = ThamSoQuyDinh(ten_qui_dinh='SoXeToiDa', gia_tri='30')
#             qd2 = ThamSoQuyDinh(ten_qui_dinh='TiLeVAT', gia_tri='0.1')
#             db.session.add_all([qd1, qd2])
#
#             # 4. Linh kiện (Bỏ ma_linh_kien)
#             lk1 = LinhKien(ten_linh_kien='Nhớt Castrol Power 1', don_gia_ban=160000, so_luong_ton=50)
#             db.session.add(lk1)
#
#             db.session.commit()
#             print(">>> XONG!")