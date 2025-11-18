from django.contrib import admin
from .models.course_model import Course
from .models.course_subject import CourseSubject
from .models.course_supervisor_model import CourseSupervisor
from .models.course_category import CourseCategory

@admin.register(CourseSubject)
class CourseSubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'subject', 'position', 'start_date')
    list_filter = ('course',)
    search_fields = ('course__name', 'subject__name')

@admin.register(CourseSupervisor)
class CourseSupervisorAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'supervisor')
    list_filter = ('course',)

@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'category')
    list_filter = ('category',)

class CourseSubjectInline(admin.TabularInline):
    model = CourseSubject
    extra = 0
    autocomplete_fields = ['subject']

class CourseSupervisorInline(admin.TabularInline):
    model = CourseSupervisor
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'finish_date', 'status', 'creator')
    search_fields = ('name',)
    list_filter = ('status',)
    inlines = [CourseSubjectInline, CourseSupervisorInline]