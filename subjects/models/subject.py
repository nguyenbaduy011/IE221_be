from django.db import models

class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    max_score = models.IntegerField()
    estimated_time_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='subject/')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
        