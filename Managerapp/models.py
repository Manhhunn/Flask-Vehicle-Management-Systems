from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# -----------------------------------------------------------
# 1. PHÂN QUYỀN
# -----------------------------------------------------------

class Role(db.Model):
    ma_role = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False)
    role_value = db.Column(db.String(50), nullable=False)

    users = db.relationship('NguoiDung', backref='role', lazy=True)


class NguoiDung(db.Model):
    ma_nguoi_dung = db.Column(db.Integer, primary_key=True)
    tai_khoan = db.Column(db.String(50), unique=True, nullable=False)
    mat_khau = db.Column(db.String(255), nullable=False)
    ho_ten = db.Column(db.String(100), nullable=False)
    user_role = db.Column(db.String(50))

    ma_role = db.Column(db.Integer, db.ForeignKey('role.ma_role'), nullable=False)


# -----------------------------------------------------------
# 2. DANH MỤC
# -----------------------------------------------------------

class LinhKien(db.Model):
    ma_linh_kien = db.Column(db.String(50), primary_key=True)
    ten_linh_kien = db.Column(db.String(100), nullable=False)
    don_gia_ban = db.Column(db.Float, nullable=False)
    so_luong_ton = db.Column(db.Integer, default=0)

    chi_tiet_sua_chua = db.relationship('ChiTietPhieuSuaChua', backref='linh_kien', lazy=True)


class TienCong(db.Model):
    ma_tien_cong = db.Column(db.Integer, primary_key=True)
    noi_dung = db.Column(db.String(255), nullable=False)
    tien_cong = db.Column(db.Float, nullable=False)

    chi_tiet_sua_chua = db.relationship('ChiTietPhieuSuaChua', backref='tien_cong', lazy=True)


class ThamSoQuyDinh(db.Model):
    ma_qui_dinh = db.Column(db.String(50), primary_key=True)
    ten_qui_dinh = db.Column(db.String(100), nullable=False)
    gia_tri = db.Column(db.String(100), nullable=False)


# -----------------------------------------------------------
# 3. QUẢN LÝ XE & TIẾP NHẬN
# -----------------------------------------------------------

class Xe(db.Model):
    ma_xe = db.Column(db.Integer, primary_key=True)
    bien_so = db.Column(db.String(20), unique=True, nullable=False)
    ten_khach_hang = db.Column(db.String(100), nullable=False)
    loai_xe = db.Column(db.String(50))
    tien_no = db.Column(db.Float, default=0.0)

    ds_phieu_tiep_nhan = db.relationship('PhieuTiepNhan', backref='xe', lazy=True)
    ds_hoa_don = db.relationship('HoaDon', backref='xe', lazy=True)


class PhieuTiepNhan(db.Model):
    ma_phieu_tiep_nhan = db.Column(db.Integer, primary_key=True)
    ngay_tiep_nhan = db.Column(db.DateTime, default=datetime.utcnow)
    loi_mo_ta = db.Column(db.String(255))

    ma_xe = db.Column(db.Integer, db.ForeignKey('xe.ma_xe'), nullable=False)
    phieu_sua_chua = db.relationship('PhieuSuaChua', backref='phieu_tiep_nhan', uselist=False, lazy=True)


# -----------------------------------------------------------
# 4. QUẢN LÝ SỬA CHỮA & CHI TIẾT
# -----------------------------------------------------------

class PhieuSuaChua(db.Model):
    ma_phieu_sua = db.Column(db.Integer, primary_key=True)
    ngay_lap = db.Column(db.DateTime, default=datetime.utcnow)
    tong_thanh_tien = db.Column(db.Float, default=0.0)

    ma_phieu_tiep_nhan = db.Column(db.Integer, db.ForeignKey('phieu_tiep_nhan.ma_phieu_tiep_nhan'), unique=True,
                                   nullable=False)

    chi_tiet = db.relationship('ChiTietPhieuSuaChua', backref='phieu_sua_chua', lazy=True)
    hoa_don = db.relationship('HoaDon', backref='phieu_sua_chua', lazy=True , uselist=False)


class ChiTietPhieuSuaChua(db.Model):
    ma_chi_tiet = db.Column(db.Integer, primary_key=True)

    hang_muc_sua_chua = db.Column(db.String(255))
    so_luong = db.Column(db.Integer, default=1)
    thue_vat = db.Column(db.Float, default=0.0)

    don_gia_luu_tru = db.Column(db.Float, default=0.0)
    tien_cong_luu_tru = db.Column(db.Float, default=0.0)
    thanh_tien = db.Column(db.Float, default=0.0)

    ma_phieu_sua = db.Column(db.Integer, db.ForeignKey('phieu_sua_chua.ma_phieu_sua'), nullable=False)
    ma_linh_kien = db.Column(db.String(50), db.ForeignKey('linh_kien.ma_linh_kien'), nullable=True)
    ma_tien_cong = db.Column(db.Integer, db.ForeignKey('tien_cong.ma_tien_cong'), nullable=True)


# -----------------------------------------------------------
# 5. THANH TOÁN
# -----------------------------------------------------------

class HoaDon(db.Model):
    ma_hoa_don = db.Column(db.Integer, primary_key=True)
    ngay_thu_tien = db.Column(db.DateTime, default=datetime.utcnow)
    thanh_toan = db.Column(db.Float, nullable=False)

    ma_xe = db.Column(db.Integer, db.ForeignKey('xe.ma_xe'), nullable=False)
    ma_phieu_sua = db.Column(db.Integer, db.ForeignKey('phieu_sua_chua.ma_phieu_sua'), nullable=True , unique =True)