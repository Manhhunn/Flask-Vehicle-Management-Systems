from datetime import datetime
import json
from flask import render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from Managerapp import app, login
import dao
from decorators import anonymous_required, admin_manager_required, sales_task_required, tech_task_required


@app.route('/')
def index():
    return render_template('index.html')


# =========================================================
# 1. AUTHENTICATION (ĐĂNG NHẬP / ĐĂNG XUẤT)
# =========================================================

@app.route('/login_account', methods=['GET', 'POST'])
@anonymous_required
def login_user_view():
    err_msg = ""
    if request.method == 'POST':
        # Gọi hàm check_login từ DAO
        user = dao.check_login(request.form.get('tai_khoan'), request.form.get('mat_khau'))
        if user:
            login_user(user)
            # Điều hướng dựa trên quyền
            if user.user_role in ['Admin', 'QuanLy']:
                return redirect('/admin')
            return redirect('/')
        else:
            err_msg = "Sai tài khoản hoặc mật khẩu!"
    return render_template('login.html', err_msg=err_msg)


@app.route('/logout')
def logout_process():
    logout_user()
    return redirect('/')


@login.user_loader
def load_user(user_id):
    return dao.get_user_by_id(user_id)


# =========================================================
# 2. ADMIN & QUẢN LÝ (TẠO TÀI KHOẢN)
# =========================================================

@app.route('/admin/create-account', methods=['GET', 'POST'])
@admin_manager_required
def admin_create_account():
    err_msg = ""
    # Lấy danh sách quyền mà user hiện tại được phép tạo
    allowed_roles = dao.get_roles_for_creator(current_user.user_role)

    if request.method == 'POST':
        try:
            dao.add_user(
                ho_ten=request.form.get('ho_ten'),
                tai_khoan=request.form.get('tai_khoan'),
                mat_khau=request.form.get('mat_khau'),
                role_id=request.form.get('role_id')
            )
            flash('Tạo tài khoản thành công!', 'success')
            return redirect('/admin')
        except Exception as e:
            err_msg = f"Lỗi: {str(e)}"

    return render_template('register.html', roles=allowed_roles, err_msg=err_msg)


@app.route('/tiep-nhan', methods=['GET', 'POST'])
@sales_task_required
def reception():
    if request.method == 'POST':
        result = dao.create_phieu_tiep_nhan(
            ma_xe=request.form.get('ma_xe'),
            nguoi_tao_id=current_user.id,
            loi_mo_ta=request.form.get('loi_mo_ta')
        )
        if result:
            flash('Tiếp nhận thành công!', 'success')
            return redirect('/')
        else:
            flash('Đã đạt giới hạn xe trong ngày (Quy định)!', 'danger')
    car = dao.get_xe_by_bien_so(request.args.get('bien_so', '').strip())
    return render_template('reception.html',car=car,search_bien_so=request.args.get('bien_so', ''),now=datetime.now())


@app.route('/them-xe', methods=['GET', 'POST'])
@sales_task_required
def add_car_view():
    if request.method == 'POST':
        try:
            dao.add_new_car(
                bien_so=request.form.get('bien_so'),
                ten_khach=request.form.get('ten_khach'),
                loai_xe=request.form.get('loai_xe')
            )
            # Thêm xong quay lại trang tiếp nhận
            return redirect(url_for('reception', bien_so=request.form.get('bien_so')))
        except Exception as e:
            flash(f'Lỗi thêm xe: {str(e)}', 'danger')

    return render_template('add_car.html', prefill_bien_so=request.args.get('bien_so', ''))


# =========================================================
# 4. NHÓM KỸ THUẬT (SỬA CHỮA)
# =========================================================

@app.route('/ky-thuat/danh-sach-tiep-nhan')
@tech_task_required
def tech_reception_list():
    # Lấy danh sách xe đang chờ sửa (chưa có phiếu sửa chữa)
    return render_template('technician/list_reception.html', receptions=dao.get_pending_reception_tickets())


@app.route('/ky-thuat/lap-phieu-sua/<int:reception_id>', methods=['GET', 'POST'])
@tech_task_required
def create_repair_ticket(reception_id):
    if request.method == 'POST':
        try:
            # Lấy dữ liệu JSON từ form (danh sách linh kiện/tiền công)
            details_data = json.loads(request.form.get('details_data'))

            dao.save_repair_ticket(reception_id, current_user.id, details_data)

            flash('Lưu phiếu sửa chữa thành công!', 'success')
            return redirect(url_for('tech_reception_list'))
        except Exception as e:
            flash(f'Lỗi: {str(e)}', 'danger')

    return render_template('technician/create_repair.html',
                           r=dao.get_reception_by_id(reception_id),
                           tax=dao.get_tax_percent())

@app.route('/nhan-vien/danh-sach-tiep-nhan')
@login_required
def view_list_reception_for_emp():
    return render_template('employee/list_recep.html', receptions=dao.get_pending_reception_tickets())


# =========================================================
# 5. API (AJAX CHO TÌM KIẾM)
# =========================================================

@app.route('/api/search-linh-kien')
@login_required
def api_search_lk():
    items = dao.search_linh_kien(request.args.get('q', ''))
    # Trả về JSON để Javascript hiển thị gợi ý
    return jsonify([{'id': x.id, 'name': x.ten_linh_kien, 'price': x.don_gia_ban , 'stock': x.so_luong_ton } for x in items])


@app.route('/api/search-tien-cong')
@login_required
def api_search_tc():
    items = dao.search_tien_cong(request.args.get('q', ''))
    return jsonify([{'id': x.id, 'name': x.noi_dung, 'price': x.tien_cong_} for x in items])


# =========================================================
# 6. NHÓM THANH TOÁN
# =========================================================

@app.route('/nhan-vien/danh-sach-thu-tien')
@sales_task_required
def invoice_list():
    # Lấy danh sách xe đang nợ tiền
    return render_template('employee/list_debt.html', cars=dao.get_cars_with_debt())


@app.route('/nhan-vien/lap-hoa-don/<int:car_id>', methods=['GET', 'POST'])
@sales_task_required
def create_invoice(car_id):
    if request.method == 'POST':
        amount = float(request.form.get('amount_paid', 0))
        repair_ticket = dao.get_unpaid_repair_ticket_by_car(car_id)
        repair_id = repair_ticket.id if repair_ticket else None

        if dao.save_invoice(car_id, repair_id, amount, current_user.id):
            flash('Thanh toán thành công!', 'success')
            return redirect(url_for('invoice_list'))
        else:
            flash('Lỗi thanh toán!', 'danger')

    return render_template('employee/payment.html',
                           car=dao.get_xe_by_id(car_id),
                           ticket=dao.get_unpaid_repair_ticket_by_car(car_id))



# =========================================================
# 7. TÍCH HỢP THANH TOÁN VNPAY (ĐÃ SỬA LỖI IMPORT)
# =========================================================
# --- API 1: TẠO URL GIẢ LẬP (BYPASS VNPAY ĐỂ TEST LOCAL) ---
@app.route('/api/payment/create_payment_url', methods=['POST'])
def create_payment_url():
    try:
        from Managerapp.models import db, HoaDon, Xe, PhieuSuaChua
        from flask_login import current_user
        from datetime import datetime

        # 1. Lấy ID Phiếu Sửa Chữa
        data = request.json
        phieu_sua_id = data.get('phieu_sua_id')

        ticket = PhieuSuaChua.query.get(phieu_sua_id)
        if not ticket:
            return jsonify({'message': 'Phiếu sửa chữa không tồn tại'}), 404

        # 2. Tự động tạo hóa đơn (nếu chưa có)
        hoa_don = HoaDon.query.filter_by(ma_phieu_sua=ticket.id).first()
        if not hoa_don:
            hoa_don = HoaDon(
                thanh_toan=ticket.tong_thanh_tien,
                ma_xe=ticket.phieu_tiep_nhan.ma_xe,
                ma_phieu_sua=ticket.id,
                nguoi_tao_id=current_user.id,
                ngay_thu_tien=datetime.now()
            )
            db.session.add(hoa_don)
            db.session.commit()


        order_ref = f"HD_{hoa_don.id}_{int(datetime.now().timestamp())}"

        # Tạo URL nội bộ: http://127.0.0.1:5000/api/payment/vnpay_return?vnp_ResponseCode=00&vnp_TxnRef=...
        fake_payment_url = url_for('vnpay_return',
                                   vnp_ResponseCode='00',
                                   vnp_TxnRef=order_ref,
                                   _external=True)

        return jsonify({'paymentUrl': fake_payment_url, 'message': 'Tạo link giả lập thành công'})

    except Exception as e:
        print(f"❌ LỖI SERVER: {str(e)}")
        return jsonify({'message': f'Lỗi server: {str(e)}'}), 500



# --- API 2: XỬ LÝ KẾT QUẢ TRẢ VỀ (PHIÊN BẢN TEST LOCAL - BỎ QUA CHECK HASH) ---
@app.route('/api/payment/vnpay_return', methods=['GET'])
def vnpay_return():
    # Import model
    from Managerapp.models import db, HoaDon

    # 1. Lấy dữ liệu từ URL trả về
    # Ví dụ URL: ...?vnp_Amount=20000000&vnp_ResponseCode=00&vnp_TxnRef=HD_50_170...
    vnp_ResponseCode = request.args.get('vnp_ResponseCode')
    vnp_TxnRef = request.args.get('vnp_TxnRef')

    # 2. Tách lấy ID Hóa đơn
    # Format mã: HD_{id}_{timestamp} (Ví dụ: HD_50_1703123456)
    try:
        parts = vnp_TxnRef.split('_')
        hoa_don_id = int(parts[1])
    except:
        return "Lỗi: Không đọc được mã hóa đơn từ VNPAY trả về", 400

    # 3. Tìm hóa đơn
    hoa_don = HoaDon.query.get(hoa_don_id)
    if not hoa_don:
        return "Lỗi: Không tìm thấy hóa đơn trong hệ thống", 404

    # 4. XỬ LÝ KẾT QUẢ (BỎ QUA CHECK HASH THEO YÊU CẦU)
    if vnp_ResponseCode == "00":
        # --- THÀNH CÔNG ---
        print(f"✅ VNPAY trả về thành công cho Hóa đơn #{hoa_don.id}. Bỏ qua check hash.")

        # Xử lý xóa nợ
        xe = hoa_don.xe
        if xe:
            xe.tien_no = 0.0
            db.session.commit()

        return render_template('employee/payment_success.html', hoa_don=hoa_don)
    else:
        # --- THẤT BẠI ---
        print(f"❌ VNPAY trả về thất bại (Code: {vnp_ResponseCode})")
        return render_template('employee/payment_failed.html', hoa_don=hoa_don)




# =========================================================
# KHỞI CHẠY
# =========================================================
if __name__ == '__main__':
    app.run(debug=True)
