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
        fields = ['id', 'name', 'max_score', 'estimated_time_days', 'image', 'tasks', 'created_at', 'updated_at']
    
    def get_tasks(self, obj):
        # Lấy task theo generic relation thủ công như logic dự án
        tasks = Task.objects.filter(taskable_type='subject', taskable_id=obj.id)
        return TaskSerializer(tasks, many=True).data