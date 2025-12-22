import hashlib
from datetime import datetime
from sqlalchemy import func
from Managerapp.models import db, Role, NguoiDung, PhieuTiepNhan, Xe, PhieuSuaChua, LinhKien, TienCong, ThamSoQuyDinh, ChiTietPhieuSuaChua, HoaDon

def get_roles():
    return Role.query.all()


def add_user(ho_ten, tai_khoan, mat_khau, role_id):
    mat_khau_hash = str(hashlib.md5(mat_khau.strip().encode("utf-8")).hexdigest())
    user = NguoiDung(ho_ten=ho_ten, tai_khoan=tai_khoan, mat_khau=mat_khau_hash, role_id=role_id)
    db.session.add(user)
    db.session.commit()
    return user


def check_user_exist(tai_khoan):
    return NguoiDung.query.filter_by(tai_khoan=tai_khoan).first()


def check_login(username, password):
    if password:
        password = str(hashlib.md5(password.strip().encode("utf-8")).hexdigest())
    return NguoiDung.query.filter_by(tai_khoan=username, mat_khau=password).first()


def get_user_by_id(user_id):
    return NguoiDung.query.get(user_id)


def get_xe_by_bien_so(bien_so):
    if not bien_so: return None
    return Xe.query.filter_by(bien_so=bien_so).first()


def add_new_car(bien_so, ten_khach, loai_xe, tien_no=0):
    xe = Xe(bien_so=bien_so, ten_khach_hang=ten_khach, loai_xe=loai_xe, tien_no=tien_no)
    db.session.add(xe)
    db.session.commit()
    return xe


# --- PHIẾU TIẾP NHẬN ---
def create_phieu_tiep_nhan(ma_xe, nguoi_tao_id, loi_mo_ta):
    # [SỬA]: Tìm theo tên quy định 'SoXeToiDa'
    max_xe_rule = ThamSoQuyDinh.query.filter_by(ma_quy_dinh='Max_XE').first()
    limit = 30
    if max_xe_rule:
        try:
            limit = int(max_xe_rule.gia_tri)
        except:
            pass

    today = datetime.now().date()
    current_count = PhieuTiepNhan.query.filter(func.date(PhieuTiepNhan.ngay_tiep_nhan) == today).count()

    if current_count >= limit: return False

    phieu = PhieuTiepNhan(ma_xe=ma_xe, nguoi_tao_id=nguoi_tao_id, loi_mo_ta=loi_mo_ta)
    db.session.add(phieu)
    db.session.commit()
    return phieu


def get_pending_reception_tickets():
    return db.session.query(PhieuTiepNhan).outerjoin(PhieuSuaChua).filter(PhieuSuaChua.id == None).all()


def get_reception_by_id(id):
    return PhieuTiepNhan.query.get(id)


# --- TÌM KIẾM ---
def search_linh_kien(keyword):
    return LinhKien.query.filter(LinhKien.ten_linh_kien.contains(keyword)).all()


def search_tien_cong(keyword):
    return TienCong.query.filter(TienCong.noi_dung.contains(keyword)).all()


def get_tax_percent():
    try:
        qd = ThamSoQuyDinh.query.filter_by(ma_quy_dinh='TiLe_VAT').first()
        if qd:
            val = float(qd.gia_tri)
            if val <= 1: return val * 100
            if val % 10 == 0: return val
            return val
        return 0.0
    except:
        return 0.0


# --- LƯU PHIẾU SỬA CHỮA ---
def save_repair_ticket(reception_id, technician_id, details_list):
    try:
        ticket = PhieuSuaChua(
            ma_phieu_tiep_nhan=reception_id,
            nguoi_tao_id=technician_id,
            ngay_lap=datetime.now(),
            tong_thanh_tien=0
        )
        db.session.add(ticket)
        db.session.flush()

        total_amount = 0
        for item in details_list:
            lk_price = 0
            tc_price = 0
            so_luong = int(item['so_luong'])  # Lấy số lượng người dùng nhập

            if item.get('linh_kien_id'):
                lk = LinhKien.query.get(item['linh_kien_id'])
                if lk:
                    if lk.so_luong_ton < so_luong:
                        raise Exception(
                            f"Linh kiện '{lk.ten_linh_kien}' không đủ hàng! (Tồn: {lk.so_luong_ton}, Cần: {so_luong})")
                    lk.so_luong_ton -= so_luong

                    lk_price = lk.don_gia_ban
            if item.get('tien_cong_id'):
                tc = TienCong.query.get(item['tien_cong_id'])  # Tìm bằng ID số
                if tc: tc_price = tc.tien_cong_

            line_total = ((lk_price + tc_price ) * int(item['so_luong']))

            detail = ChiTietPhieuSuaChua(
                ma_phieu_sua=ticket.id,
                hang_muc_sua_chua=item['hang_muc'],
                linh_kien_id=item['linh_kien_id'] if item['linh_kien_id'] else None,
                tien_cong_id=item['tien_cong_id'] if item['tien_cong_id'] else None,
                so_luong=so_luong,
                don_gia_luu_tru=lk_price,
                tien_cong_luu_tru=tc_price,
                thanh_tien=line_total
            )
            db.session.add(detail)
            total_amount += line_total

        # Tính thuế & Update xe
        tax_percent = get_tax_percent()
        final_total = total_amount * (1 + tax_percent / 100)
        ticket.tong_thanh_tien = final_total

        reception = PhieuTiepNhan.query.get(reception_id)
        car = Xe.query.get(reception.ma_xe)
        car.tien_no += final_total

        db.session.commit()
        return ticket
    except Exception as e:
        db.session.rollback()
        raise e


# --- THANH TOÁN ---
def get_cars_with_debt():
    return Xe.query.filter(Xe.tien_no > 0).all()


def get_xe_by_id(car_id):
    return Xe.query.get(car_id)



def get_unpaid_repair_ticket_by_car(car_id):
    return db.session.query(PhieuSuaChua) \
        .join(PhieuTiepNhan, PhieuSuaChua.ma_phieu_tiep_nhan == PhieuTiepNhan.id) \
        .filter(PhieuTiepNhan.ma_xe == car_id) \
        .order_by(PhieuSuaChua.ngay_lap.desc()) \
        .first()


def save_invoice(car_id, repair_id, amount_paid, creator_id):
    try:
        invoice = HoaDon(
            ngay_thu_tien=datetime.now(),
            thanh_toan=amount_paid,
            ma_xe=car_id,
            ma_phieu_sua=repair_id,
            nguoi_tao_id=creator_id
        )
        db.session.add(invoice)

        # Xóa nợ
        car = Xe.query.get(car_id)
        if car: car.tien_no = 0

        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


# --- HỖ TRỢ ---
def get_roles_for_creator(user_role_value):
    all_roles = Role.query.all()
    if user_role_value == 'Admin':
        return [r for r in all_roles if r.role_value != 'Admin']
    elif user_role_value == 'QuanLy':
        return [r for r in all_roles if r.role_value in ['NhanVien', 'KyThuatVien']]
    return []


# --- THỐNG KÊ (Giữ nguyên) ---
def stats_revenue_by_year(year):
    return db.session.query(
        func.extract('month', HoaDon.ngay_thu_tien),
        func.sum(HoaDon.thanh_toan)
    ).filter(func.extract('year', HoaDon.ngay_thu_tien) == year) \
        .group_by(func.extract('month', HoaDon.ngay_thu_tien)) \
        .order_by(func.extract('month', HoaDon.ngay_thu_tien)).all()


def stats_car_ratio():
    return db.session.query(Xe.loai_xe, func.count(Xe.id)).group_by(Xe.loai_xe).all()


def stats_common_faults():
    return db.session.query(
        TienCong.noi_dung, func.count(ChiTietPhieuSuaChua.id)
    ).join(ChiTietPhieuSuaChua, ChiTietPhieuSuaChua.tien_cong_id == TienCong.id) \
        .group_by(TienCong.noi_dung) \
        .order_by(func.count(ChiTietPhieuSuaChua.id).desc()).limit(5).all()

