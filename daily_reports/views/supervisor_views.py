from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
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
        supervised_courses = user.supervised_courses.values_list('id', flat=True)
        queryset = DailyReport.objects.filter(course_id__in=supervised_courses)
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
