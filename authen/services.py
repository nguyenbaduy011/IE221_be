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
    
    activation_link = f"http://localhost:3000/activate/{uidb64}/{token}/"
    
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