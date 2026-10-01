# Flask Vehicle Management Systems

Hệ thống quản lý garage / trung tâm sửa chữa ô tô được xây dựng bằng Flask, hỗ trợ quản lý thông tin xe, tiếp nhận xe, lập phiếu sửa chữa, xử lý hóa đơn và tích hợp thanh toán VNPAY (mô phỏng test local).

## Tóm tắt dự án

Dự án này nhằm xây dựng một phần mềm quản lý vận hành garage/đại lý sửa chữa ô tô với các chức năng chính:

- Đăng nhập / phân quyền người dùng
- Quản lý tài khoản theo vai trò: Admin, Quản lý, Nhân viên, Kỹ thuật viên
- Tiếp nhận xe vào garage
- Thêm mới thông tin xe khách hàng
- Lập phiếu sửa chữa và chi tiết linh kiện / tiền công
- Theo dõi xe đang nợ tiền và lập hóa đơn thanh toán
- Tích hợp chuyển hướng thanh toán VNPAY mẫu cho môi trường cục bộ

## Công nghệ sử dụng

- Python 3
- Flask
- Flask-Login
- Flask-SQLAlchemy
- MySQL / MariaDB
- PyMySQL
- Jinja2 Templates
- HTML / CSS / JavaScript

## Cấu trúc thư mục

```text
Flask-Vehicle-Management-Systems/
├── Managerapp/
│   ├── __init__.py              # Khởi tạo app Flask và cấu hình DB
│   ├── admin.py                 # Logic quản trị / phân quyền / thao tác admin
│   ├── app.py                   # Các route chính của ứng dụng
│   ├── dao.py                   # Lớp truy vấn dữ liệu và nghiệp vụ
│   ├── models.py                # Model ORM / bảng dữ liệu
│   ├── decorators.py            # Decorator kiểm tra quyền truy cập
│   ├── vnpay.py                 # Module tích hợp VNPAY
│   ├── static/                  # File tĩnh (CSS, JS, hình ảnh...)
│   └── templates/               # Templates HTML của ứng dụng
│       ├── admin/
│       ├── employee/
│       ├── technician/
│       ├── layout/
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── reception.html
│       └── add_car.html
├── requirements.txt             # Các dependency cần cài đặt
├── .gitignore
└── README.md
```

## Tính năng chính

### 1. Xác thực và phân quyền
- Đăng nhập cho người dùng
- Chia quyền theo chức vụ:
  - Admin
  - Quản lý
  - Nhân viên
  - Kỹ thuật viên
- Quyền truy cập được kiểm soát bằng decorator trong `decorators.py`

### 2. Quản lý xe
- Thêm xe mới
- Tìm kiếm thông tin xe theo biển số
- Tiếp nhận xe vào gara
- Ghi nhận mô tả lỗi ban đầu

### 3. Quản lý sửa chữa
- Lập phiếu tiếp nhận
- Kỹ thuật viên tạo phiếu sửa chữa
- Chọn linh kiện và tiền công theo từng hạng mục
- Tính tổng thành tiền tự động

### 4. Hóa đơn và thanh toán
- Theo dõi xe đang nợ tiền
- Tạo hóa đơn thanh toán
- Cập nhật trạng thái nợ của xe
- Hỗ trợ mô phỏng link thanh toán VNPAY test local

### 5. Giao diện web
- Dùng templates Jinja2
- UI theo cấu trúc phân quyền
- Có các trang riêng cho admin, nhân viên, kỹ thuật viên

## Cài đặt

### Yêu cầu
- Python 3.10+
- MySQL 8.0+
- Pip

### Bước 1: Clone repository

```bash
git clone https://github.com/Manhhunn/Flask-Vehicle-Management-Systems.git
cd Flask-Vehicle-Management-Systems
```

### Bước 2: Tạo môi trường ảo

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
# hoặc
venv\Scripts\activate      # Windows
```

### Bước 3: Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### Bước 4: Cấu hình MySQL

Mở file `Managerapp/__init__.py` và cập nhật chuỗi kết nối database:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:MAT_KHAU_CUA_BAN@localhost/cnpmdb5?charset=utf8mb4"
```

Ví dụ:

```python
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:123456@localhost/cnpmdb5?charset=utf8mb4"
```

Lưu ý:
- Đảm bảo MySQL đã được chạy
- Database `cnpmdb5` đã tồn tại hoặc bạn tạo mới trước khi chạy app

### Bước 5: Tạo schema database

Từ thư mục gốc, chạy Python sau:

```bash
python -c "from Managerapp import app
from Managerapp.models import db
with app.app_context():
    db.create_all()
    print('Database initialized successfully!')"
```

### Bước 6: Chạy ứng dụng

```bash
python Managerapp/app.py
```

Ứng dụng sẽ chạy tại:

```text
http://127.0.0.1:5000
```

## Tài khoản mặc định

Trong file `models.py` có phần seed dữ liệu đã được comment sẵn. Nếu bạn muốn tạo dữ liệu mẫu, hãy uncomment và chạy script khởi tạo một lần.

Ví dụ tài khoản admin mẫu:

- Tài khoản: `admin`
- Mật khẩu: `123456`

## Quy trình sử dụng cơ bản

1. Truy cập trang đăng nhập
2. Đăng nhập bằng tài khoản phù hợp
3. Nếu là Admin/Quản lý, tạo tài khoản mới cho nhân sự
4. Nhân viên tiếp nhận xe vào garage
5. Kỹ thuật viên lập phiếu sửa chữa
6. Nhân viên lập hóa đơn và thanh toán
7. Hệ thống cập nhật trạng thái nợ và thanh toán

## Lưu ý về VNPAY

Dự án hiện có tích hợp VNPAY dạng mock/test local trong route:

- `/api/payment/create_payment_url`
- `/api/payment/vnpay_return`

Đây là phiên bản phục vụ môi trường kiểm thử local, không phải triển khai production đầy đủ.

## Ghi chú

- Dự án đang sử dụng cấu hình cố định trong code thay vì `.env` file
- Nếu bạn muốn triển khai production, nên chuyển các thông tin nhạy cảm như DB credentials, secret key và cấu hình VNPAY ra file môi trường
- Nên kiểm tra và cập nhật `secret_key` trước khi deploy lên môi trường thật

## Liên hệ / đóng góp

Nếu bạn muốn phát triển thêm các chức năng như:
- export hóa đơn PDF
- báo cáo thống kê doanh thu
- upload ảnh xe/sửa chữa
- tích hợp VNPAY đúng chuẩn production

bạn có thể mở rộng dự án dựa trên cấu trúc hiện có.

## License

Dự án này hiện chưa có file license rõ ràng. Nếu cần, bạn có thể thêm một giấy phép phù hợp như MIT hoặc GPL.
