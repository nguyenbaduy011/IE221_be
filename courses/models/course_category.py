from django.db import models
from subjects.models.category import Category

class CourseCategory(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'category')

    def __str__(self):
        return f"{self.course.name} - {self.category.name}"