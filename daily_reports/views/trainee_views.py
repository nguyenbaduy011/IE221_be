from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils import timezone
from ..models import DailyReport
from ..serializers import DailyReportSerializer


class TraineeDailyReportViewSet(viewsets.ModelViewSet):
    serializer_class = DailyReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        token_payload = self.request.auth

        token_user_id = token_payload.get("user_id")
        if not token_user_id:
            raise PermissionDenied("Invalid token: missing user_id")

        if not hasattr(user, "role") or user.role != "TRAINEE":
            raise PermissionDenied("You are not allowed to access trainee reports.")

        queryset = DailyReport.objects.filter(user=user)

        course_id = self.request.query_params.get("course_id")
        filter_date = self.request.query_params.get("filter_date")

        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if filter_date:
            queryset = queryset.filter(created_at__date=filter_date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.status != 0:
            raise ValidationError("Cannot delete a submitted report.")
        instance.delete()

    def perform_update(self, serializer):
        if serializer.instance.status != 0:
            raise ValidationError("Cannot edit a submitted report.")
        serializer.save()
