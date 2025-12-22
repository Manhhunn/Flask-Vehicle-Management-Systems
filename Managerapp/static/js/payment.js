document.addEventListener('DOMContentLoaded', function() {
    // ---------------------------------------------------------
    // 1. GUARD CLAUSE
    // Chỉ chạy code nếu tìm thấy Form Thanh Toán
    // ---------------------------------------------------------
    const paymentForm = document.getElementById('paymentForm');
    if (!paymentForm) return;

    // ---------------------------------------------------------
    // 2. LẤY CÁC ELEMENT CẦN THIẾT
    // ---------------------------------------------------------
    const radios = document.querySelectorAll('input[name="payment_method"]');

    // Các khu vực hiển thị
    const divCash = document.getElementById('actionCash');
    const divQR = document.getElementById('actionQR');

    // Các nút bấm (Label)
    const lblCash = document.getElementById('lblCash');
    const lblQR = document.getElementById('lblQR');

    // [MỚI] Các Element phục vụ VNPAY
    const btnVNPAY = document.getElementById('btnPayVNPAY'); // Nút tạo QR
    const hiddenInvoiceId = document.getElementById('hiddenInvoiceId'); // ID hóa đơn ẩn

    // ---------------------------------------------------------
    // 3. HÀM XỬ LÝ GIAO DIỆN (Toggle UI) - (GIỮ NGUYÊN)
    // ---------------------------------------------------------
    function updatePaymentUI() {
        const selected = document.querySelector('input[name="payment_method"]:checked').value;

        if (selected === 'tien_mat') {
            // -- Chế độ TIỀN MẶT --
            if(divCash) divCash.style.display = 'block';
            if(divQR) divQR.style.display = 'none';

            if(lblCash) {
                lblCash.classList.add('bg-success', 'bg-opacity-10', 'border-success');
                lblCash.classList.remove('text-muted');
            }
            if(lblQR) {
                lblQR.classList.remove('bg-primary', 'bg-opacity-10', 'border-primary');
                lblQR.classList.add('text-muted');
            }

        } else {
            // -- Chế độ QR / CHUYỂN KHOẢN --
            if(divCash) divCash.style.display = 'none';
            if(divQR) divQR.style.display = 'block';

            if(lblCash) {
                lblCash.classList.remove('bg-success', 'bg-opacity-10', 'border-success');
                lblCash.classList.add('text-muted');
            }
            if(lblQR) {
                lblQR.classList.add('bg-primary', 'bg-opacity-10', 'border-primary');
                lblQR.classList.remove('text-muted');
            }
        }
    }

    // ---------------------------------------------------------
    // 4. GẮN SỰ KIỆN CHO UI
    // ---------------------------------------------------------
    radios.forEach(radio => {
        radio.addEventListener('change', updatePaymentUI);
    });

    // Xử lý nút LƯU TIỀN MẶT (Form Submit)
    paymentForm.addEventListener('submit', function(e) {
        // Thêm confirm để tránh bấm nhầm
        const confirmed = confirm("Xác nhận đã nhận đủ tiền mặt từ khách hàng?");
        if (!confirmed) {
            e.preventDefault(); // Hủy gửi form nếu chọn Cancel
        } else {
            // Để form tự submit lên server
            // alert("Đang xử lý hoá đơn...");
        }
    });

    // ---------------------------------------------------------
    // 5. [MỚI] XỬ LÝ NÚT THANH TOÁN VNPAY (Async/Await)
    // ---------------------------------------------------------
    if (btnVNPAY) {
        btnVNPAY.addEventListener('click', async function(e) {
            e.preventDefault(); // Ngăn hành vi mặc định (nếu có)

            // Kiểm tra ID hóa đơn
            if (!hiddenInvoiceId || !hiddenInvoiceId.value) {
                alert("Lỗi: Không tìm thấy mã hóa đơn (ID)!");
                return;
            }

            // Hiệu ứng Loading
            const originalText = btnVNPAY.innerHTML;
            btnVNPAY.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang kết nối VNPAY...';
            btnVNPAY.disabled = true;

            try {
                // Gọi API Python
                const response = await fetch('/api/payment/create_payment_url', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        phieu_sua_id: hiddenInvoiceId.value
                    })
                });

                const result = await response.json();

                if (response.ok && result.paymentUrl) {
                    // Thành công -> Chuyển hướng sang VNPAY
                    window.location.href = result.paymentUrl;
                } else {
                    // Thất bại -> Báo lỗi
                    alert(result.message || "Có lỗi xảy ra khi tạo liên kết thanh toán!");
                    // Reset nút bấm
                    btnVNPAY.innerHTML = originalText;
                    btnVNPAY.disabled = false;
                }

            } catch (error) {
                console.error("Lỗi kết nối:", error);
                alert("Không thể kết nối đến server. Vui lòng kiểm tra mạng!");

                // Reset nút bấm
                btnVNPAY.innerHTML = originalText;
                btnVNPAY.disabled = false;
            }
        });
    }

    // ---------------------------------------------------------
    // 6. KHỞI TẠO UI LẦN ĐẦU
    // ---------------------------------------------------------
    updatePaymentUI();
});