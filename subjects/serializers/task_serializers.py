from rest_framework import serializers
from courses.models.course_subject import CourseSubject
from subjects.models.task import Task
from subjects.models.subject import Subject

class TaskSerializer(serializers.ModelSerializer):
    subject_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Task
        fields = ['id', 'name', 'subject_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        name = data.get('name')
        subject_id = data.get('subject_id')

        if self.instance:
            if not name:
                name = self.instance.name
            if not subject_id:
                if self.instance.taskable_type == Task.TaskType.SUBJECT:
                     subject_id = self.instance.taskable_id

        if name and subject_id:
            exists = Task.objects.filter(
                name__iexact=name,
                taskable_type=Task.TaskType.SUBJECT,
                taskable_id=subject_id
            ).exclude(id=self.instance.id if self.instance else None).exists()

            if exists:
                raise serializers.ValidationError("Task name already exists for this subject.")

        return data

    def validate_subject_id(self, value):
        if not Subject.objects.filter(id=value).exists():
            raise serializers.ValidationError("Subject not found.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.taskable_type == Task.TaskType.SUBJECT:
            representation['subject_id'] = instance.taskable_id
            representation['type'] = 'Subject Task'
            try:
                representation['subject_name'] = Subject.objects.get(id=instance.taskable_id).name
            except Subject.DoesNotExist:
                representation['subject_name'] = "Unknown"

        elif instance.taskable_type == Task.TaskType.COURSE_SUBJECT:
            try:
                cs = CourseSubject.objects.get(id=instance.taskable_id)
                representation['subject_id'] = cs.subject_id
                representation['subject_name'] = cs.subject.name
                representation['course_id'] = cs.course_id
                representation['type'] = 'Course Subject Task'
            except CourseSubject.DoesNotExist:
                representation['subject_id'] = None
                representation['subject_name'] = "Unknown"

        return representation

    def create(self, validated_data):
        subject_id = validated_data.pop('subject_id')
        task = Task.objects.create(
            name=validated_data['name'],
            taskable_type=Task.TaskType.SUBJECT,
            taskable_id=subject_id
        )
        return task

    def update(self, instance, validated_data):
        if 'subject_id' in validated_data:
            instance.taskable_id = validated_data.pop('subject_id')

        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance
