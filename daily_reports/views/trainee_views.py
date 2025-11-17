from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone
from ..models import DailyReport
from ..serializers import DailyReportSerializer


class TraineeDailyReportViewSet(viewsets.ModelViewSet):
    """
    - GET /trainee/daily_reports/ (list)
    - POST /trainee/daily_reports/ (create)
    - GET /trainee/daily_reports/{id}/ (show)
    - PUT/PATCH /trainee/daily_reports/{id}/ (update)
    - DELETE /trainee/daily_reports/{id}/ (destroy)
    """
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        token_payload = self.request.auth

        # Lấy user_id từ token
        token_user_id = token_payload.get("user_id")
        if not token_user_id:
            raise PermissionDenied("Invalid token: missing user_id")

        # Kiểm tra role trainee
        if not hasattr(user, "role") or user.role != "trainee":
            raise PermissionDenied("You are not allowed to access trainee reports.")

        # Chỉ lấy báo cáo của chính user
        queryset = DailyReport.objects.filter(user=user)

        # Filter thêm nếu có
        course_id = self.request.query_params.get("course_id")
        filter_date = self.request.query_params.get("filter_date")

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        return queryset

    def perform_create(self, serializer):
        # Tự gán user từ token
        serializer.save(user=self.request.user)
