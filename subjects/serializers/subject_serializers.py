from rest_framework import serializers
from django.db import transaction
from subjects.models.subject import Subject
from subjects.models.task import Task

class TaskSimpleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False) 

    class Meta:
        model = Task
        fields = ['id', 'name', 'position']

class SubjectSerializer(serializers.ModelSerializer):
    tasks = TaskSimpleSerializer(many=True, required=False)

    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'max_score', 'estimated_time_days', 
            'image', 'tasks', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'max_score': {'required': False},
            'estimated_time_days': {'required': False},
        }

    @transaction.atomic
    def create(self, validated_data):
        tasks_data = validated_data.pop('tasks', [])
        
        subject = Subject.objects.create(**validated_data)

        if tasks_data:
            for index, task_item in enumerate(tasks_data):
                Task.objects.create(
                    name=task_item['name'],
                    taskable_type=Task.TaskType.SUBJECT,
                    taskable_id=subject.id,
                    position=index + 1
                )
        
        return subject

    @transaction.atomic
    def update(self, instance, validated_data):
        tasks_data = validated_data.pop('tasks', None)

        instance.name = validated_data.get('name', instance.name)
        instance.max_score = validated_data.get('max_score', instance.max_score)
        instance.estimated_time_days = validated_data.get('estimated_time_days', instance.estimated_time_days)
        if validated_data.get('image'):
            instance.image = validated_data.get('image')
        instance.save()

        if tasks_data is not None:
            current_tasks = Task.objects.filter(
                taskable_type=Task.TaskType.SUBJECT,
                taskable_id=instance.id
            )
            current_task_ids = set(t.id for t in current_tasks)
            incoming_task_ids = set(item['id'] for item in tasks_data if 'id' in item)

            ids_to_delete = current_task_ids - incoming_task_ids
            if ids_to_delete:
                Task.objects.filter(id__in=ids_to_delete).delete()

            for index, task_item in enumerate(tasks_data):
                task_id = task_item.get('id')
                
                if task_id and task_id in current_task_ids:
                    task = Task.objects.get(id=task_id)
                    task.name = task_item.get('name', task.name)
                    task.position = index + 1 
                    task.save()
                else:
                    Task.objects.create(
                        name=task_item['name'],
                        taskable_type=Task.TaskType.SUBJECT,
                        taskable_id=instance.id,
                        position=index + 1
                    )

        return instance