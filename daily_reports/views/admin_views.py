from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from ..models import DailyReport
from ..serializers import DailyReportSerializer


class AdminDailyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - GET /admin/daily_reports/
    - GET /admin/daily_reports/{id}/
    """
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]   # tự kiểm tra role

    def get_queryset(self):
        user = self.request.user
        token_payload = self.request.auth   # payload JWT

        # Lấy user_id từ token
        user_id = token_payload.get("user_id")

        # Nếu không có user_id => token lỗi
        if not user_id:
            raise PermissionDenied("Invalid token: missing user_id")

        # KIỂM TRA ROLE USER
        # giả sử User model có trường `role`
        if not hasattr(user, "role") or user.role != "ADMIN":
            raise PermissionDenied("You do not have permission to access this resource.")

        # User hợp lệ => trả dữ liệu
        queryset = DailyReport.objects.all()

        # Các filter khác
        course_id = self.request.query_params.get('course_id')
        filter_date = self.request.query_params.get('filter_date')

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        # ❗ Không cho client truyền user_id trong query => bỏ luôn
        return queryset
