# authen/services.py
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

def send_activation_email(user, request):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    activation_link = f"{settings.CLIENT_URL}/activate/{uidb64}/{token}/"
    
    subject = "Kích hoạt tài khoản của bạn"
    message = f"""
    Chào {user.full_name},
    
    Vui lòng click vào link sau để kích hoạt tài khoản của bạn:
    {activation_link}
    
    Trân trọng.
    """
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

def send_new_account_email(user, password):
    """
    Gửi email thông báo tài khoản mới được tạo bởi Admin.
    """
    login_url = f"{settings.CLIENT_URL}/auth/login" # Đường dẫn tới trang đăng nhập
    
    subject = "Thông tin tài khoản của bạn tại Hệ thống"
    message = f"""
    Chào {user.full_name},

    Tài khoản của bạn đã được quản trị viên tạo thành công.
    Dưới đây là thông tin đăng nhập của bạn:

    ----------------------------------------
    Email: {user.email}
    Mật khẩu: {password}
    ----------------------------------------

    Vui lòng đăng nhập tại: {login_url}
    Lưu ý: Vì lý do bảo mật, hãy đổi mật khẩu ngay sau khi đăng nhập lần đầu.

    Trân trọng,
    Đội ngũ quản trị.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )