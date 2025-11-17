from django.db import models
from django.utils import timezone
from authen.models import CustomUser

class UserCourse(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, "Not Started"
        IN_PROGRESS = 1, "In Progress"
        FINISH = 2, "Finish"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_courses')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='user_courses')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)
    joined_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.FINISH and not self.finished_at:
            self.finished_at = timezone.now()
        super().save(*args, **kwargs)