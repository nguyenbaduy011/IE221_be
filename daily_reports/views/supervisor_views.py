from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from ..models import DailyReport
from ..serializers import DailyReportSerializer


class SupervisorDailyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - GET /supervisor/daily_reports/
    - GET /supervisor/daily_reports/{id}/
    """
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        token_payload = self.request.auth   # JWT payload

        # Lấy user_id từ token
        token_user_id = token_payload.get("user_id")
        if not token_user_id:
            raise PermissionDenied("Invalid token: missing user_id")

        # 🚨 Kiểm tra role supervisor
        # giả sử User model có `role`
        if not hasattr(user, "role") or user.role != "supervisor":
            raise PermissionDenied("You are not allowed to access supervisor reports.")

        # Lấy danh sách khóa học mà supervisor đang giám sát
        supervised_courses = user.supervised_courses.values_list("id", flat=True)

        # Queryset mặc định
        queryset = DailyReport.objects.filter(course_id__in=supervised_courses)

        # Optional filters
        course_id = self.request.query_params.get("course_id")
        filter_date = self.request.query_params.get("filter_date")

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        # ❌ KHÔNG cho truyền user_id qua query param → xóa luôn
        # Mọi DailyReport đều đã tự động giới hạn theo course_id supervised.

        return queryset
