from rest_framework.views import exception_handler
from rest_framework.response import Response

def custom_exception_handler(exc, context):
    # Lấy response lỗi mặc định của DRF
    response = exception_handler(exc, context)

    # Nếu DRF có response (lỗi 4xx, 5xx)
    if response is not None:
        
        # Đây là cấu trúc chuẩn JSend (hoặc của riêng bạn)
        standard_response = {
            "status": "error", # Hoặc "fail" nếu là 400
            "message": "",
            "errors": None
        }

        if response.status_code == 400: # Lỗi Validation
            standard_response["status"] = "fail"
            standard_response["message"] = "Dữ liệu không hợp lệ."
            standard_response["errors"] = response.data # { "email": [...] }
        elif response.status_code == 401:
            standard_response["message"] = "Xác thực thất bại."
            standard_response["errors"] = response.data
        elif response.status_code == 404:
            standard_response["message"] = "Không tìm thấy tài nguyên."
            standard_response["errors"] = response.data
        else: # Lỗi 500
            standard_response["message"] = "Đã xảy ra lỗi hệ thống."

        # Ghi đè response.data
        response.data = standard_response

    return response