from rest_framework import serializers
from courses.models.course_subject import CourseSubject
from subjects.models.task import Task
from subjects.models.subject import Subject

class TaskSerializer(serializers.ModelSerializer):
    # Field này chỉ dùng để nhận input (write_only), client gửi lên 'subject_id'
    subject_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = Task
        # Output trả về id, name, created_at và subject_id (được xử lý trong to_representation)
        fields = ['id', 'name', 'subject_id', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate_subject_id(self, value):
        """
        Kiểm tra xem Subject có tồn tại không trước khi tạo Task
        """
        if not Subject.objects.filter(id=value).exists():
            raise serializers.ValidationError("Subject not found.")
        return value
    
    def to_representation(self, instance):
        """
        Custom output: Luôn trả về 'subject_id' dù taskable_type là gì
        """
        representation = super().to_representation(instance)
        
        if instance.taskable_type == Task.TaskType.SUBJECT:
            # Nếu là Task của Subject, taskable_id chính là subject_id
            representation['subject_id'] = instance.taskable_id
            representation['type'] = 'Subject Task'
            
        elif instance.taskable_type == Task.TaskType.COURSE_SUBJECT:
            # Nếu là Task của CourseSubject, query ngược lại để lấy subject_id
            # Lưu ý: Việc này có thể gây N+1 query nếu list quá dài, nên tối ưu queryset bằng prefetch_related nếu cần
            try:
                cs = CourseSubject.objects.get(id=instance.taskable_id)
                representation['subject_id'] = cs.subject_id
                representation['course_id'] = cs.course_id # Optional: trả thêm course_id
                representation['type'] = 'Course Subject Task'
            except CourseSubject.DoesNotExist:
                representation['subject_id'] = None

        return representation

    def create(self, validated_data):
        """
        Logic tạo task: 
        - Lấy subject_id ra khỏi data.
        - Gán taskable_type = 0 (Task.TaskType.SUBJECT).
        - Gán taskable_id = subject_id.
        """
        subject_id = validated_data.pop('subject_id')
        
        task = Task.objects.create(
            name=validated_data['name'],
            taskable_type=Task.TaskType.SUBJECT, # Yêu cầu: fix cứng type là Subject (0)
            taskable_id=subject_id
        )
        return task

    def update(self, instance, validated_data):
        """
        Logic update task.
        Cho phép đổi subject (chuyển task sang subject khác) nếu cần.
        """
        if 'subject_id' in validated_data:
            instance.taskable_id = validated_data.pop('subject_id')
        
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def to_representation(self, instance):
        """
        Custom output: Trả về 'subject_id' cho frontend thay vì 'taskable_id'
        để thống nhất format dữ liệu.
        """
        representation = super().to_representation(instance)
        if instance.taskable_type == Task.TaskType.SUBJECT:
            representation['subject_id'] = instance.taskable_id
        return representation