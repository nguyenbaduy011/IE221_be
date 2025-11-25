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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        token_payload = self.request.auth

        user_id = token_payload.get("user_id")
        if not user_id:
            raise PermissionDenied("Invalid token: missing user_id")

        if not hasattr(user, "role") or user.role != "ADMIN":
            raise PermissionDenied("You do not have permission to access this resource.")

        queryset = (
            DailyReport.objects
            .filter(status=1)
            .select_related("course", "user")
        )

        course_id = self.request.query_params.get("course_id")
        filter_date = self.request.query_params.get("filter_date")

        if course_id:
            queryset = queryset.filter(course_id=course_id)

        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        return queryset
