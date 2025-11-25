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
        token_payload = self.request.auth

        token_user_id = token_payload.get("user_id")
        if not token_user_id:
            raise PermissionDenied("Invalid token: missing user_id")

        if not hasattr(user, "role") or user.role != "SUPERVISOR":
            raise PermissionDenied("You are not allowed to access supervisor reports.")

        supervised_courses = user.supervised_courses.values_list("id", flat=True)

        queryset = (
            DailyReport.objects
            .filter(course_id__in=supervised_courses)
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
