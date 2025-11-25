from rest_framework.renderers import JSONRenderer

class CustomJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')
        if response and 200 <= response.status_code < 300: 
            response_data = {
                "status": "success",
                "message": "Thành công",
                "data": None,
                "errors": None
            }
            if data is not None:
                if isinstance(data, dict) and 'message' in data and len(data) == 1:
                    response_data['message'] = data['message']
                elif isinstance(data, dict) and 'data' in data and 'message' in data:
                     response_data['data'] = data['data']
                     response_data['message'] = data['message']
                else:
                    response_data['data'] = data
            return super().render(response_data, accepted_media_type, renderer_context)
        return super().render(data, accepted_media_type, renderer_context)