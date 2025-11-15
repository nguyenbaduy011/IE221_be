from django.db import models
from subjects.models.subject import Subject

class CourseSubject(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('course', 'subject')
        ordering = ['position']

    def __str__(self):
        return f"{self.course.name} - {self.subject.name}"