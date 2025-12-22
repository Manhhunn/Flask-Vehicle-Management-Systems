let rowCount = 0;

document.addEventListener('DOMContentLoaded', function() {
    addRow(); // Thêm sẵn 1 dòng khi mở trang
});

function getTaxRate() {
    const form = document.getElementById('repairForm');
    return parseFloat(form.getAttribute('data-tax-rate')) || 0;
}

// 1. HÀM THÊM DÒNG (Cấu trúc 9 cột bao gồm SL)
function addRow() {
    rowCount++;
    const tbody = document.getElementById('tableBody');

    const row = `
        <tr id="row_${rowCount}">
            <td class="text-center bg-light">${rowCount}</td>
            
            <td>
                <input type="text" class="form-control" name="hang_muc" placeholder="Nhập tên...">
            </td>
            
            <td class="position-relative">
                <input type="text" class="form-control" placeholder="Tìm LK..." 
                       onkeyup="searchLK(this, ${rowCount})" autocomplete="off">
                <div class="list-group position-absolute w-100" id="list_lk_${rowCount}" style="z-index:1000; display:none;"></div>
                <input type="hidden" name="linh_kien_id" id="lk_id_${rowCount}">
            </td>
            
            <td>
                <input type="number" class="form-control text-end bg-light" id="lk_price_${rowCount}" value="0" readonly tabindex="-1">
            </td>
            
            <td class="position-relative">
                <input type="text" class="form-control" placeholder="Tìm TC..." 
                       onkeyup="searchTC(this, ${rowCount})" autocomplete="off">
                <div class="list-group position-absolute w-100" id="list_tc_${rowCount}" style="z-index:1000; display:none;"></div>
                <input type="hidden" name="tien_cong_id" id="tc_id_${rowCount}">
            </td>
            
            <td>
                <input type="number" class="form-control text-end bg-light" id="tc_price_${rowCount}" value="0" readonly tabindex="-1">
            </td>
            
            <td>
                <input type="number" class="form-control text-center fw-bold" name="so_luong" value="1" min="1" onchange="calcTotal()" onkeyup="calcTotal()">
            </td>
            
            <td>
                <input type="text" class="form-control text-end fw-bold text-primary" id="row_total_${rowCount}" value="0" readonly tabindex="-1">
            </td>
            
            <td class="text-center">
                <button type="button" class="btn btn-danger btn-sm" onclick="removeRow(${rowCount})"><i class="fas fa-trash"></i></button>
            </td>
        </tr>
    `;
    tbody.insertAdjacentHTML('beforeend', row);
}

// 2. XÓA DÒNG
function removeRow(id) {
    const row = document.getElementById(`row_${id}`);
    if(row) { row.remove(); calcTotal(); }
}

// 3. TÌM KIẾM LINH KIỆN (Đã sửa đổi)
async function searchLK(input, id) {
    const keyword = input.value;
    const listDiv = document.getElementById(`list_lk_${id}`);
    if (keyword.length < 2) { listDiv.style.display = 'none'; return; }

    try {
        const res = await fetch(`/api/search-linh-kien?q=${keyword}`);
        const data = await res.json();
        listDiv.innerHTML = '';

        if(data.length > 0){
            listDiv.style.display = 'block';
            data.forEach(item => {
                const a = document.createElement('a');
                a.className = 'list-group-item list-group-item-action';

                const stockBadge = item.stock > 0
                    ? `<span class="badge bg-info me-2">Tồn: ${item.stock}</span>`
                    : `<span class="badge bg-danger me-2">Hết hàng</span>`;

                a.innerHTML = `${item.name} <br> ${stockBadge} <span class="badge bg-secondary float-end">${item.price.toLocaleString()}</span>`;
                a.href = '#';

                // Sự kiện khi chọn linh kiện
                a.onclick = (e) => {
                    e.preventDefault();

                    if(item.stock <= 0) {
                        alert("Sản phẩm này đã hết hàng, không thể chọn!");
                        return;
                    }

                    input.value = item.name;
                    document.getElementById(`lk_id_${id}`).value = item.id;
                    document.getElementById(`lk_price_${id}`).value = item.price;

                    // LƯU TRỮ SỐ LƯỢNG TỒN VÀO MỘT THUỘC TÍNH ẨN ĐỂ CHECK SAU
                    // Input số lượng ở dòng này sẽ biết max là bao nhiêu
                    const qtyInput = document.querySelector(`#row_${id} input[name="so_luong"]`);
                    qtyInput.setAttribute('data-max-stock', item.stock);
                    qtyInput.max = item.stock; // (Tuỳ chọn) Chặn HTML5

                    listDiv.style.display = 'none';
                    calcTotal();
                };
                listDiv.appendChild(a);
            });
        } else { listDiv.style.display = 'none'; }
    } catch (error) { console.error(error); }
}
// 4. TÌM KIẾM TIỀN CÔNG
async function searchTC(input, id) {
    const keyword = input.value;
    const listDiv = document.getElementById(`list_tc_${id}`);
    if (keyword.length < 2) { listDiv.style.display = 'none'; return; }

    try {
        const res = await fetch(`/api/search-tien-cong?q=${keyword}`);
        const data = await res.json();
        listDiv.innerHTML = '';

        if(data.length > 0) {
            listDiv.style.display = 'block';
            data.forEach(item => {
                const a = document.createElement('a');
                a.className = 'list-group-item list-group-item-action';
                a.innerHTML = `${item.name} <span class="badge bg-secondary float-end">${item.price.toLocaleString()}</span>`;
                a.href = '#';
                a.onclick = (e) => {
                    e.preventDefault();
                    input.value = item.name;
                    document.getElementById(`tc_id_${id}`).value = item.id;
                    document.getElementById(`tc_price_${id}`).value = item.price; // Điền giá vào cột Số tiền công
                    listDiv.style.display = 'none';
                    calcTotal();
                };
                listDiv.appendChild(a);
            });
        } else { listDiv.style.display = 'none'; }
    } catch (error) { console.error(error); }
}

// 5. TÍNH TỔNG (Logic: (LK + TC) * SL)
function calcTotal() {
    let grandTotal = 0;
    const rows = document.querySelectorAll('#tableBody tr');

    rows.forEach(row => {
        const rowId = row.id.split('_')[1];
        const lkPrice = parseFloat(document.getElementById(`lk_price_${rowId}`).value) || 0;
        const tcPrice = parseFloat(document.getElementById(`tc_price_${rowId}`).value) || 0;
        const qty = parseFloat(row.querySelector('input[name="so_luong"]').value) || 0;

        const rowSum = (lkPrice + tcPrice) * qty;

        document.getElementById(`row_total_${rowId}`).value = rowSum.toLocaleString();
        grandTotal += rowSum;
    });

    const taxRate = getTaxRate();
    const taxAmount = grandTotal * (taxRate / 100);
    const final = grandTotal + taxAmount;

    document.getElementById('sumTotal').innerText = grandTotal.toLocaleString();
    document.getElementById('taxValue').innerText = taxAmount.toLocaleString();
    document.getElementById('finalTotal').innerText = final.toLocaleString() + ' VND';
}

// 6. CHUẨN BỊ DỮ LIỆU GỬI ĐI
function prepareData(e) {
    const rows = document.querySelectorAll('#tableBody tr');
    const data = [];

    let isEmptyError = false; // Cờ lỗi để trống dòng
    let isStockError = false; // Cờ lỗi vượt quá tồn kho

    // 1. Check nếu không có dòng nào
    if (rows.length === 0) {
        alert("Vui lòng nhập ít nhất 1 dòng!");
        e.preventDefault();
        return;
    }

    rows.forEach((row, index) => {
        // Lấy các element input để thao tác class CSS (tô đỏ nếu lỗi)
        const qtyInput = row.querySelector('input[name="so_luong"]');
        const hangMucInput = row.querySelector('input[name="hang_muc"]');

        // Lấy giá trị
        const item = {
            hang_muc: hangMucInput.value.trim(),
            linh_kien_id: row.querySelector('input[name="linh_kien_id"]').value || null,
            tien_cong_id: row.querySelector('input[name="tien_cong_id"]').value || null,
            so_luong: parseFloat(qtyInput.value) || 0
        };


        if (!item.hang_muc && !item.linh_kien_id && !item.tien_cong_id) {
            isEmptyError = true;
            hangMucInput.classList.add('is-invalid'); // Tô đỏ ô tên hạng mục
        } else {
            hangMucInput.classList.remove('is-invalid');
        }

        if (item.linh_kien_id) {
            const maxStockStr = qtyInput.getAttribute('data-max-stock');

            if (maxStockStr !== null && maxStockStr !== "") {
                const maxStock = parseFloat(maxStockStr);

                if (item.so_luong > maxStock) {
                    isStockError = true;
                    qtyInput.classList.add('is-invalid'); // Tô đỏ ô số lượng
                    // (Tuỳ chọn) Thêm tooltip nhắc nhở
                    qtyInput.setAttribute('title', `Tồn kho chỉ còn: ${maxStock}`);
                } else {
                    qtyInput.classList.remove('is-invalid');
                    qtyInput.removeAttribute('title');
                }
            }
        }

        data.push(item);
    });

    // 2. Xử lý thông báo lỗi cuối cùng
    if (isEmptyError || isStockError) {
        e.preventDefault(); // Chặn gửi form

        if (isStockError) {
            alert("Lỗi: Có dòng nhập quá số lượng tồn kho! Vui lòng kiểm tra các ô màu đỏ.");
        } else {
            alert("Lỗi: Dòng dữ liệu không được để trống thông tin!");
        }
        return;
    }

    // 3. Nếu mọi thứ OK -> Gán dữ liệu vào input hidden
    document.getElementById('detailsData').value = JSON.stringify(data);
}