# 🏫 LMS -- Hệ thống Quản lý Đào tạo Nội bộ Doanh nghiệp (Backend)

## Tổng quan

Đây là dự án với Backend được xây dựng bằng **Django**, phục vụ cho hệ thống LMS nội bộ doanh nghiệp. Ứng dụng cung cấp giao diện người dùng cho các chức năng như quản lý khóa học, người dùng, lớp học, bài kiểm tra, báo cáo học tập và các hoạt động đào tạo nội bộ.

## Yêu cầu hệ thống

- Python 3.8 trở lên
- pip (trình quản lý gói Python)
- PostgreSQL

## Cài đặt

### 1. Clone repository

```bash
git clone https://github.com/nguyenbaduy011/IE221_be
cd IE221_be
```

### 2. Cài đặt dependencies

Chạy lệnh sau để cài tất cả các package cần thiết:

```bash
pip install -r requirements.txt
```

### 3. Thiết lập biến môi trường

#### Bước 1: Tạo file `.env`

Sao chép file `.env.example` để tạo file `.env`:

```bash
cp .env.example .env
```

#### Bước 2: Cấu hình file `.env`

Chỉnh sửa file `.env` và điền các giá trị cần thiết:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASS=your-database-password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_TLS=False
EMAIL_USE_SSL=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

##### Chi tiết các trường:

| Trường | Giải thích | Ví dụ |
|--------|-----------|-------|
| **DEBUG** | Chế độ debug (True cho phát triển, False cho production) | `True` |
| **SECRET_KEY** | Khóa bí mật Django (dùng `django.core.management.utils.get_random_secret_key()`) | `your-random-secret-key` |
| **DB_ENGINE** | Engine cơ sở dữ liệu | `django.db.backends.postgresql` |
| **DB_NAME** | Tên database PostgreSQL | `your-database-name` |
| **DB_USER** | Tên người dùng PostgreSQL | `your-database-user` |
| **DB_PASS** | Mật khẩu PostgreSQL | `your-database-password` |
| **DB_HOST** | Host của PostgreSQL | `localhost` |
| **DB_PORT** | Port của PostgreSQL | `5432` |
| **EMAIL_HOST** | SMTP server để gửi email | `smtp.gmail.com` |
| **EMAIL_PORT** | Port SMTP | `465` |
| **EMAIL_USE_TLS** | Dùng TLS | `False` |
| **EMAIL_USE_SSL** | Dùng SSL | `True` |
| **EMAIL_HOST_USER** | Email để gửi từ | `your-email@gmail.com` |
| **EMAIL_HOST_PASSWORD** | App password Gmail (không phải mật khẩu thường) | `your-app-password` |

#### Bước 3: Tạo Secret Key (nếu không có)

Chạy lệnh này trong Django shell để tạo SECRET_KEY mới:

```bash
python manage.py shell
```

Trong shell:

```python
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Copy giá trị và paste vào file `.env`.

#### Bước 4: Cấu hình PostgreSQL

Đảm bảo PostgreSQL đang chạy và tạo database:

```bash
# Kết nối vào PostgreSQL
psql -U postgres

# Trong psql, chạy các lệnh:
CREATE DATABASE your-database-name;
CREATE USER your-database-user WITH PASSWORD 'your-secure-password';
ALTER ROLE your-database-user SET client_encoding TO 'utf8';
ALTER ROLE your-database-user SET default_transaction_isolation TO 'read committed';
ALTER ROLE your-database-user SET default_transaction_deferrable TO on;
ALTER ROLE your-database-user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE your-database-name TO your-database-user;
\q
```

**Lưu ý:** Thay thế `your-database-name`, `your-database-user`, và `your-secure-password` bằng các giá trị thực tế của bạn. Các giá trị này phải khớp với những gì bạn đặt trong file `.env`.

#### Bước 5: Cấu hình Email Gmail (tuỳ chọn)

Để sử dụng Gmail gửi email:

1. Truy cập [Google Account Security](https://myaccount.google.com/security)
2. Bật "2-Step Verification" nếu chưa bật
3. Tạo "App password" cho ứng dụng
4. Copy mật khẩu ứng dụng 16 ký tự vào `EMAIL_HOST_PASSWORD` trong `.env`

### 4. Cấu hình cơ sở dữ liệu

Sau khi cấu hình file `.env`, chạy migrations:

```bash
python manage.py migrate
```

#### (Tuỳ chọn) Khởi tạo dữ liệu mẫu

```bash
python manage.py seed_data
```

### 5. Chạy server phát triển

```bash
python manage.py runserver
```

Ứng dụng sẽ chạy tại: `http://127.0.0.1:8000/`

## Lưu ý quan trọng

- **KHÔNG** commit file `.env` lên repository (nó đã được thêm vào `.gitignore`)
- Luôn sử dụng các biến môi trường cho thông tin nhạy cảm
- Mỗi thành viên trong team cần có file `.env` riêng của họ
- **KHÔNG** chia sẻ mật khẩu database hoặc secret key qua chat, email

## Troubleshooting

Nếu gặp lỗi kết nối database, kiểm tra:
- PostgreSQL có đang chạy không
- Tên database, user, password có chính xác không
- DB_HOST và DB_PORT có đúng không