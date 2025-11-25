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

    response = exception_handler(exc, context)

    if response is not None:

        custom_response_data = {
            "status": "error",    
            "code": None,
            "message": None,        
            "data": None,          
            "errors": None       
        }

        if hasattr(exc, 'get_codes'):
            code = exc.get_codes()
           
            if isinstance(code, str):
                custom_response_data["code"] = code.upper()
     
        if response.status_code == 400:
            custom_response_data["status"] = "fail"
            custom_response_data["message"] = "Dữ liệu đầu vào không hợp lệ."
            custom_response_data["errors"] = response.data
            
        elif response.status_code == 401:
            custom_response_data["message"] = "Bạn chưa đăng nhập hoặc phiên đăng nhập hết hạn."
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

        response.data = custom_response_data

    return response