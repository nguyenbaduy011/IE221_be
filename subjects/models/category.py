from django.db import models
from .subject import Subject

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    subjects = models.ManyToManyField(Subject, through='SubjectCategory', related_name='categories')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name