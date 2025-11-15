from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .course_model import Course

class CourseSupervisor(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='supervisors')
    supervisor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='supervised_courses_links')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Đảm bảo rằng mỗi cặp (khóa học, người giám sát) là duy nhất.
        """
        unique_together = ('course', 'supervisor')
        ordering = ['-created_at']

    def clean(self):
        """
        Đảm bảo rằng mỗi khóa học có ít nhất một người giám sát.
        """
        if self.pk and self.course:
            remaining = self.course.supervisors.exclude(pk=self.pk).count()
            if remaining < 1:
                raise ValidationError(
                    _("Course must have at least one supervisor.")
                )

    def delete(self, *args, **kwargs):
        """
        Ghi đè phương thức xóa để đảm bảo rằng việc xóa người giám sát không vi phạm quy tắc.
        """
        self.clean()
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.supervisor.email} supervises {self.course.name}"