from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    max_score = models.IntegerField(default=0)
    estimated_time_days = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='subject/', null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    @property
    def tasks(self):
        from subjects.models.task import Task
        return Task.objects.filter(
            taskable_type=Task.TaskType.SUBJECT,
            taskable_id=self.id
        ).order_by('position')