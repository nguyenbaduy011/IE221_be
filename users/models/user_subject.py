from django.db import models
from django.utils import timezone
from authen.models import CustomUser
from subjects.models.subject import Subject

class UserSubject(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, "Not Started"
        IN_PROGRESS = 1, "In Progress"
        FINISH = 2, "Finish"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='user_subjects')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'subject')

    def __str__(self):
        return f"{self.user.email} - {self.subject.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        if self.status == self.Status.FINISH and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)