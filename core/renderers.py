# core/renderers.py
from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        
        # Nếu response là thành công (200-299)
        if response and 200 <= response.status_code < 300:
            
            # Cấu trúc chuẩn
            response_data = {
                "status": "success",
                "message": "Thành công",
                "data": None,
                "errors": None
            }

            # Logic xử lý dữ liệu trả về từ View
            if data is not None:
                # Trường hợp 1: View trả về dict có chứa key 'message' (chủ động set message)
                # Ví dụ: return Response({"message": "Đổi mật khẩu thành công"})
                if isinstance(data, dict) and 'message' in data and len(data) == 1:
                    response_data['message'] = data['message']
                
                # Trường hợp 2: View trả về dict có 'data' và 'message' (kiểu cũ)
                elif isinstance(data, dict) and 'data' in data and 'message' in data:
                     response_data['data'] = data['data']
                     response_data['message'] = data['message']

                # Trường hợp 3: View trả về dữ liệu bình thường (Object, List, Token...)
                else:
                    response_data['data'] = data

            return super().render(response_data, accepted_media_type, renderer_context)

        # Nếu là lỗi (4xx, 5xx), ExceptionHandler đã xử lý format rồi,
        # Renderer chỉ việc trả về nguyên vẹn.
        return super().render(data, accepted_media_type, renderer_context)