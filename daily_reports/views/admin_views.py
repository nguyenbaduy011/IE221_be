from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from ..models import DailyReport
from ..serializers import DailyReportSerializer

class AdminDailyReportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    - GET /admin/daily_reports/
    - GET /admin/daily_reports/{id}/
    """
    serializer_class = DailyReportSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = DailyReport.objects.all()
        course_id = self.request.query_params.get('course_id')
        filter_date = self.request.query_params.get('filter_date')
        user_id = self.request.query_params.get('user_id')

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset
