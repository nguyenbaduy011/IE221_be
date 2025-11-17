from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from .managers import CustomUserManager 
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError

class CustomUser(AbstractBaseUser, PermissionsMixin):
    
    class Role(models.TextChoices):
        TRAINEE = "TRAINEE", "Trainee"
        SUPERVISOR = "SUPERVISOR", "Supervisor"
        ADMIN = "ADMIN", "Admin"

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=50, choices=Role.choices)

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    birthday = models.DateField(null=True, blank=True)
    gender = models.IntegerField(null=True, blank=True) 

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class UserCourse(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, "Not Started"
        IN_PROGRESS = 1, "In Progress"
        FINISH = 2, "Finish"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_courses')
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='user_courses')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)
    joined_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user.email} - {self.course.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.FINISH and not self.finished_at:
            self.finished_at = timezone.now()
        super().save(*args, **kwargs)

class UserSubject(models.Model):
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, "Not Started"
        IN_PROGRESS = 1, "In Progress"
        FINISH = 2, "Finish"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_subjects')
    subject = models.ForeignKey('subjects.Subject', on_delete=models.CASCADE, related_name='user_subjects')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)
    score = models.FloatField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'subject')

    def __str__(self):
        return f"{self.user.email} - {self.subject.name}"

    def save(self, *args, **kwargs):
        if self.status == self.Status.IN_PROGRESS and not self.started_at:
            self.started_at = timezone.now()
        if self.status == self.Status.FINISH and not self.completed_at:
            self.completed_at = timezone.now()
        super().save(*args, **kwargs)

class UserTask(models.Model):
    class Status(models.IntegerChoices):
        DONE = 1, "Done"
        NOT_DONE = 0, "Not Done"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_tasks')
    task = models.ForeignKey('subjects.Task', on_delete=models.CASCADE, related_name='user_tasks')
    user_subject = models.ForeignKey(UserSubject, on_delete=models.CASCADE, related_name='user_tasks')
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_DONE)
    spent_time = models.FloatField(null=True, blank=True)  # in hours
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'task')

    def __str__(self):
        return f"{self.user.email} - {self.task.name}"

    def clean(self):
        if self.spent_time is not None and self.spent_time < 0:
            raise ValidationError("Spent time cannot be negative.")

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    commentable = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Comment by {self.user.email} on {self.content_type} {self.object_id}"

    def clean(self):
        if not self.content.strip():
            raise ValidationError("Comment content cannot be empty.")
        
        if len(self.content) < 5:
            raise ValidationError("Comment content must be at least 5 characters long.")

        if len(self.content) > 500:
            raise ValidationError("Comment content cannot exceed 500 characters.")
