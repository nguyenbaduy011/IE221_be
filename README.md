# Django Project README

## Tổng quan

Đây là một dự án web sử dụng Django. Dự án cung cấp hệ thống LMS online cho nội bộ doanh nghiệp.

## Yêu cầu hệ thống

-   Python 3.8 trở lên
-   pip (trình quản lý gói Python)
-   PostgreSQL

## Cài đặt

1.  **Clone repository**:

    ``` bash
    git clone https://github.com/nguyenbaduy011/IE229_be
    cd IE229_be
    ```

2.  **Thiết lập biến môi trường**:

    -   Sao chép file `.env.example` và tạo file `.env`:

        ``` bash
        cp .env.example .env
        ```

    -   Chỉnh sửa file `.env` để điền các cấu hình cần thiết (ví dụ:
        thông tin database, secret key, v.v.).\
        Ví dụ các trường trong `.env.example`:

            SECRET_KEY=your-secret-key
            DATABASE_URL=your-database-url
            DEBUG=True

3.  **Cài đặt dependencies**:\
    Chạy lệnh sau để cài tất cả các package cần thiết:

    ``` bash
    pip install -r requirements.txt
    ```

4.  **Cấu hình cơ sở dữ liệu**:

    -   Đảm bảo thông tin cấu hình trong file `.env` là chính xác.

    -   Chạy migrations để tạo bảng:

        ``` bash
        python manage.py migrate
        ```

    -   (Tuỳ chọn) Khởi tạo dữ liệu mẫu: Users, Courses, Subjects, ...

        ``` bash
        python manage.py seed_data
        ```

5.  **Chạy server phát triển**:

    ``` bash
    python manage.py runserver
    ```

    Ứng dụng sẽ chạy tại:\
    👉 `http://127.0.0.1:8000/`
