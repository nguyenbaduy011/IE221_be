from django.contrib import admin
from .models.user_course import UserCourse
from .models.user_subject import UserSubject
from .models.user_task import UserTask
from .models.comment import Comment

@admin.register(UserCourse)
class UserCourseAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'status', 'joined_at', 'finished_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'course__name')

@admin.register(UserSubject)
class UserSubjectAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'status', 'score')
    list_filter = ('status',)

@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'status')
    list_filter = ('status',)

admin.site.register(Comment)