# core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

from django.core.exceptions import ObjectDoesNotExist
from authen.models import CustomUser
def custom_exception_handler(exc, context):

    if isinstance(exc, CustomUser.DoesNotExist) or isinstance(exc, ObjectDoesNotExist):
        return Response({
            "status": "error",
            "code": "USER_NOT_FOUND",
            "message": "Tài khoản không tồn tại hoặc đã bị xóa.",
            "data": None,
            "errors": None
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Gọi handler mặc định của DRF để lấy response cơ bản trước
    response = exception_handler(exc, context)

    # Nếu DRF đã bắt được lỗi (response không None)
    if response is not None:
        
        # Cấu trúc chuẩn cho mọi lỗi
        custom_response_data = {
            "status": "error",      # Luôn là error/fail
            "code": None,
            "message": None,        # Thông báo lỗi chung
            "data": None,           # Thường là null khi lỗi
            "errors": None          # Chi tiết lỗi (cho dev/frontend debug)
        }

        if hasattr(exc, 'get_codes'):
            code = exc.get_codes()
            # get_codes() có thể trả về string, dict hoặc list. 
            # Với AuthenticationFailed đơn giản, nó thường là string.
            if isinstance(code, str):
                custom_response_data["code"] = code.upper()
        # -------------------------------------------------

        # 1. Xử lý message dựa trên Status Code
        if response.status_code == 400:
            custom_response_data["status"] = "fail"
            custom_response_data["message"] = "Dữ liệu đầu vào không hợp lệ."
            custom_response_data["errors"] = response.data # Chi tiết field nào sai
            
        elif response.status_code == 401:
            custom_response_data["message"] = "Bạn chưa đăng nhập hoặc phiên đăng nhập hết hạn."
            # Xử lý riêng cho code 'account_not_active' của bạn
            if isinstance(response.data, dict) and response.data.get('code') == 'ACCOUNT_NOT_ACTIVE':
                custom_response_data["message"] = "Tài khoản chưa được kích hoạt."
            custom_response_data["errors"] = response.data

        elif response.status_code == 403:
            custom_response_data["message"] = "Bạn không có quyền thực hiện hành động này."
            
        elif response.status_code == 404:
            custom_response_data["message"] = "Không tìm thấy tài nguyên."
            
        else:
            custom_response_data["message"] = "Đã xảy ra lỗi."
            custom_response_data["errors"] = response.data

        # Ghi đè data của response
        response.data = custom_response_data

    return response