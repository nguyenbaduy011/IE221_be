from django.contrib import admin
from .models.subject import Subject
from .models.category import Category
from .models.task import Task
from .models.subject_category import SubjectCategory

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_score')
    search_fields = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('name', 'taskable_type', 'taskable_id')
    list_filter = ('taskable_type',)
    search_fields = ('name',)

admin.site.register(Category)
admin.site.register(SubjectCategory)