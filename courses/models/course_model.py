from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class Course(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'
        IN_PROGRESS = 1, 'In Progress'
        FINISHED = 2, 'Finished'

    name = models.CharField(max_length=100, unique=True)
    link_to_course = models.URLField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='courses/', null=True, blank=True)
    start_date = models.DateField()
    finish_date = models.DateField()
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_courses')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    course_supervisors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='CourseSupervisor',
        related_name='supervised_courses'
    )

    def clean(self):
        if self.finish_date < self.start_date:
            raise ValidationError("Finish date cannot be earlier than start date.")

    def save(self, *args, **kwargs):
        today = date.today()
        if self.start_date and self.finish_date:
            if today < self.start_date:
                self.status = self.Status.NOT_STARTED
            elif self.start_date <= today <= self.finish_date:
                self.status = self.Status.IN_PROGRESS
            else:
                self.status = self.Status.FINISHED
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
