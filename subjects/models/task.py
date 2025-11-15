from django.db import models

class Task(models.Model):
    name = models.CharField(max_length=255)

    taskable_type = models.CharField(max_length=50)
    taskable_id = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['taskable_type', 'taskable_id']),
        ]