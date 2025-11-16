# core/renderers.py
from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        
        # Chỉ bọc lại các response thành công (2xx)
        if 200 <= response.status_code < 300:
            
            # Cấu trúc response chuẩn
            response_data = {
                "status": "success",
                "data": None,
                "message": None
            }

            if isinstance(data, dict):
                # 1. Lấy 'data' và 'message' từ dict mà View trả về
                response_data['data'] = data.get('data')
                response_data['message'] = data.get('message')

                # 2. Nếu cả hai đều không có, nghĩa là View đã trả về 
                # data thô (ví dụ: UserProfileView)
                if response_data['data'] is None and response_data['message'] is None:
                    response_data['data'] = data
            
            # 3. Nếu View trả về 1 list (ví dụ: ListAPIView)
            elif isinstance(data, list):
                response_data['data'] = data
            
            # 4. Xóa các key bị None để response sạch hơn
            response_data = {k: v for k, v in response_data.items() if v is not None}
            
            return super().render(response_data, accepted_media_type, renderer_context)
        
        else:
            # Lỗi (4xx, 5xx) đã được Exception Handler xử lý
            # Chỉ cần render 'data' (đã được format)
            return super().render(data, accepted_media_type, renderer_context)