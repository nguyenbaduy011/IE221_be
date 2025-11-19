from django.db import models
from django.utils import timezone
from authen.models import CustomUser
from courses.models.course_subject import CourseSubject
from users.models.user_course import UserCourse

class UserSubject(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, "Not Started"
        IN_PROGRESS = 1, "In Progress"
        FINISHED_EARLY = 2, "Finished early"
        FINISHED_ON_TIME = 3, "Finished on time"
        FINISED_BUT_OVERDUE = 4, "Finished but overdue"
        OVERDUE_AND_NOT_FINISHED = 5, "Overdue and not finished"


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_subjects')
    user_course = models.ForeignKey(UserCourse, on_delete=models.CASCADE, related_name='user_subjects')
    course_subject = models.ForeignKey(CourseSubject, on_delete=models.CASCADE, related_name='user_subjects')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course_subject', 'user_course')

    def __str__(self):
        return f"{self.user.email} - {self.subject.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.IN_PROGRESS and self.started_at is None:
            self.started_at = timezone.now()
        if self.status in [self.Status.FINISHED_EARLY, self.Status.FINISHED_ON_TIME, self.Status.FINISED_BUT_OVERDUE] and self.completed_at is None:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)