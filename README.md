# 💰 Personal Finance Tracker

Ứng dụng quản lý tài chính cá nhân với đầy đủ tính năng theo dõi thu chi, ngân sách và báo cáo.

## 📋 Tính Năng

### 1. ✅ Authentication
- Đăng ký / Đăng nhập / Đăng xuất
- JWT Authentication (Flask-JWT-Extended)
- Protected routes

### 2. ✅ Dashboard (Trang chính)
- Số dư hiện tại
- Tổng thu nhập / chi tiêu tháng này
- Biểu đồ cột thu/chi 6 tháng gần đây
- Biểu đồ tròn chi tiêu theo danh mục
- Giao dịch gần đây

### 3. ✅ Quản lý Giao Dịch
- Thêm / Sửa / Xóa giao dịch (Income / Expense)
- Danh sách có phân trang
- Lọc theo: Ngày, Tháng, Năm, Loại, Danh mục
- Tìm kiếm theo mô tả
- Export CSV

### 4. ✅ Danh Mục
- Danh mục thu nhập (Lương, Thưởng, Đầu tư...)
- Danh mục chi tiêu (Ăn uống, Đi lại, Mua sắm...)
- Tùy chỉnh màu sắc và icon
- Thêm / Sửa / Xóa danh mục

### 5. ✅ Ngân Sách (Bonus)
- Đặt ngân sách cho từng danh mục theo tháng
- Hiển thị % đã dùng so với ngân sách
- Cảnh báo khi vượt ngân sách

### 6. ✅ Báo Cáo & Export
- Báo cáo thu/chi theo tháng/năm
- Biểu đồ chi tiêu theo danh mục
- Export danh sách giao dịch ra CSV

---

## 🛠️ Công Nghệ

### Backend
- **Flask** - Python web framework
- **MySQL** - Database
- **Flask-JWT-Extended** - JWT Authentication
- **Flask-Bcrypt** - Password hashing
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **HTML5 / CSS3 / JavaScript** (Vanilla)
- **Tailwind CSS** - UI Framework
- **Chart.js** - Biểu đồ
- **Font Awesome** - Icons

---

## 📦 Cài Đặt

### Yêu cầu
- Python 3.8+
- MySQL 5.7+
- Node.js (không bắt buộc, chỉ cần browser)

### Bước 1: Clone hoặc tải project

```bash
# Nếu dùng git
git clone <repo-url>
cd "Personal Finance Tracker"
```

### Bước 2: Cài đặt Python dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Bước 3: Cấu hình Database

Tạo file `.env` trong thư mục `backend/`:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=finance_tracker

SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here
```

Tạo database MySQL:

```sql
CREATE DATABASE finance_tracker CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### Bước 4: Khởi tạo Database

```bash
python database.py
```

### Bước 5: Chạy Backend Server

```bash
python app.py
```

Server sẽ chạy tại `http://localhost:5000`

### Bước 6: Mở Frontend

Mở file `frontend/index.html` trong trình duyệt (hoặc dùng Live Server trong VS Code).

---

## 📁 Cấu Trúc Dự Án

```
Personal Finance Tracker/
├── backend/
│   ├── app.py                  # Flask app entry point
│   ├── database.py             # Database connection & initialization
│   ├── .env.example            # Environment variables template
│   └── routes/
│       ├── auth_routes.py      # Đăng ký, đăng nhập, đăng xuất
│       ├── transaction_routes.py # CRUD giao dịch
│       ├── category_routes.py  # CRUD danh mục
│       ├── budget_routes.py    # CRUD ngân sách
│       ├── dashboard_routes.py # Dashboard data
│       └── report_routes.py    # Báo cáo & Export CSV
├── frontend/
│   ├── index.html              # Trang đăng nhập/đăng ký
│   ├── dashboard.html          # Trang dashboard
│   ├── transactions.html       # Trang quản lý giao dịch
│   ├── categories.html         # Trang quản lý danh mục
│   ├── budgets.html            # Trang quản lý ngân sách
│   ├── reports.html            # Trang báo cáo
│   ├── css/
│   │   └── style.css           # Custom styles
│   └── js/
│       ├── app.js              # API helper, auth, utilities
│       ├── dashboard.js        # Dashboard logic
│       ├── transactions.js     # Transactions logic
│       ├── categories.js       # Categories logic
│       ├── budgets.js          # Budgets logic
│       └── reports.js          # Reports logic
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

---

## 🚀 API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký
- `POST /api/auth/login` - Đăng nhập
- `GET /api/auth/me` - Thông tin user hiện tại

### Transactions
- `GET /api/transactions` - Danh sách giao dịch (có phân trang, lọc)
- `POST /api/transactions` - Thêm giao dịch
- `PUT /api/transactions/:id` - Sửa giao dịch
- `DELETE /api/transactions/:id` - Xóa giao dịch

### Categories
- `GET /api/categories` - Danh sách danh mục
- `POST /api/categories` - Thêm danh mục
- `PUT /api/categories/:id` - Sửa danh mục
- `DELETE /api/categories/:id` - Xóa danh mục

### Budgets
- `GET /api/budgets` - Danh sách ngân sách tháng
- `POST /api/budgets` - Thêm/cập nhật ngân sách
- `DELETE /api/budgets/:id` - Xóa ngân sách

### Dashboard
- `GET /api/dashboard/summary` - Tổng hợp dashboard

### Reports
- `GET /api/reports/monthly` - Báo cáo theo tháng
- `GET /api/reports/category` - Báo cáo theo danh mục
- `GET /api/reports/export/csv` - Export CSV

---

## 📝 Ghi Chú

- Tất cả API endpoints (trừ `/api/auth/register`, `/api/auth/login`) đều yêu cầu JWT token trong header: `Authorization: Bearer <token>`
- Database sẽ tự động tạo bảng và danh mục mặc định khi đăng ký user mới
- Số tiền được lưu dạng DECIMAL(12,2) trong database
- Mặc định hiển thị tiền VNĐ

---

## 🎯 Roadmap (Tính Năng Tương Lai)

- [ ] Dark mode
- [ ] Recurring transactions
- [ ] Multi-currency support
- [ ] Data backup/restore
- [ ] Mobile app (React Native)
- [ ] Charts: Line chart xu hướng thu chi
- [ ] Notification khi vượt ngân sách
- [ ] Chia sẻ ngân sách gia đình

---

## 👨‍💻 Phát Triển Bởi

Được xây dựng bởi dontdevops bằng Flask + Vanilla JS + Tailwind CSS

---

## 📄 License

MIT License
