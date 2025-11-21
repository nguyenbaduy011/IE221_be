from django.db import models

class Task(models.Model):
    class TaskType(models.IntegerChoices):
        SUBJECT = 0, 'Subject'
        COURSE_SUBJECT = 1, 'CourseSubject'

    name = models.CharField(max_length=255)
    taskable_type = models.IntegerField(choices=TaskType.choices)
    taskable_id = models.PositiveIntegerField()
    position = models.PositiveIntegerField(default=0) 
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['taskable_type', 'taskable_id']),
        ]
        ordering = ['position', 'created_at']