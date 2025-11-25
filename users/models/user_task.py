from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from authen.models import CustomUser
from users.models.user_subject import UserSubject
from subjects.models.task import Task

class UserTask(models.Model):
    class Status(models.IntegerChoices):
        DONE = 1, "Done"
        NOT_DONE = 0, "Not Done"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='user_tasks')
    user_subject = models.ForeignKey(UserSubject, on_delete=models.CASCADE, related_name='user_tasks')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_DONE)
    spent_time = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submission_file = models.FileField(upload_to='submissions/%Y/%m/%d/', null=True, blank=True)


    class Meta:
        unique_together = ('user', 'task')

    def __str__(self):
        return f"{self.user.email} - {self.task.name}"

    def clean(self):
        if self.spent_time is not None and self.spent_time < 0:
            raise ValidationError("Spent time cannot be negative.")

    def save(self, *args, **kwargs):
        if self.spent_time:
            self.spent_time = round(self.spent_time, 1)
        super().save(*args, **kwargs)

    def clean(self):
        if self.spent_time is not None and self.spent_time < 0:
            raise ValidationError("Spent time cannot be negative.")
