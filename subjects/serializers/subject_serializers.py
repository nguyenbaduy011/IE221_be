from rest_framework import serializers
from subjects.models.subject import Subject
from subjects.models.task import Task


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'name', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = [
            'id',
            'name',
            'max_score',
            'estimated_time_days',
            'image',
            'tasks',
            'created_at',
            'updated_at'
        ]

    def get_tasks(self, obj):
        # Lọc task theo enum INTEGER, không dùng string
        tasks = Task.objects.filter(
            taskable_type=Task.TaskType.SUBJECT,
            taskable_id=obj.id
        )
        return TaskSerializer(tasks, many=True).data
