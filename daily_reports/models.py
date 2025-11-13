from django.db import models
from django.conf import settings
from courses.models.course_model import Course

class DailyReport(models.Model):
    STATUS_CHOICES = [
        (0, 'draft'),
        (1, 'submitted'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_reports')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='daily_reports')
    content = models.TextField(blank=True, null=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'daily_reports'
        indexes = [
            models.Index(fields=['user', 'course']),
            models.Index(fields=['course']),
        ]
        ordering = ['-updated_at']

    def __str__(self):
        return f"{self.user} - {self.course} ({self.get_status_display()})"

    def clean(self):
        from django.core.exceptions import ValidationError
        from django.utils import timezone

        today = timezone.now().date()
        if DailyReport.objects.filter(
            user=self.user,
            course=self.course,
            created_at__date=today
        ).exclude(pk=self.pk).exists():
            raise ValidationError("A report already exists for this course today.")
