from django.db import models

class SubjectCategory(models.Model):
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE)
    category = models.ForeignKey('subjects.Category', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('subject', 'category')
        ordering = ['position']