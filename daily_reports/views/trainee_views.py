from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
        queryset = DailyReport.objects.filter(user=user)
        course_id = self.request.query_params.get('course_id')
        filter_date = self.request.query_params.get('filter_date')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
