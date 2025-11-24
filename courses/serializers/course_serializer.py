from rest_framework import serializers
from authen.models import CustomUser
from django.db import transaction
from courses.models.course_model import Course
from users.models.user_course import UserCourse
from courses.models.course_subject import CourseSubject
from courses.models.course_supervisor_model import CourseSupervisor
from subjects.models.task import Task
from subjects.models.subject import Subject
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "full_name"]


# 1. Serializer cho Task
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name"]


# 2. Serializer cho Subject
class SubjectDetailSerializer(serializers.ModelSerializer):
    # Lấy danh sách task thuộc subject này
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ["id", "name", "estimated_time_days", "image", "max_score", "tasks"]

    def get_tasks(self, obj):
        # Logic lấy task của bạn (tuỳ vào model Task bạn quan hệ thế nào)
        # Ví dụ: return TaskSerializer(obj.tasks.all(), many=True).data
        # Giả sử bạn có property 'tasks' trong model Subject như code cũ:
        return TaskSerializer(obj.tasks, many=True).data


class CourseSupervisorSerializer(serializers.ModelSerializer):
    supervisor = UserBasicSerializer(read_only=True)

    class Meta:
        model = CourseSupervisor
        fields = ["id", "supervisor", "created_at"]


class CourseSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectDetailSerializer(read_only=True)

    class Meta:
        model = CourseSubject
        # Thêm start_date, finish_date, status vào fields
        fields = [
            "id",
            "course",
            "subject",
            "position",
            "start_date",
            "finish_date",
        ]


class CourseSerializer(serializers.ModelSerializer):
    supervisor_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    supervisors = CourseSupervisorSerializer(many=True, read_only=True)

    course_subjects = CourseSubjectSerializer(
        many=True, read_only=True, source="coursesubject_set"
    )

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "link_to_course",
            "image",
            "start_date",
            "finish_date",
            "status",
            "created_at",
            "updated_at",
            "supervisors",
            "course_subjects",
            "supervisor_count",
            "member_count",
        ]

    def get_supervisor_count(self, obj):
        return CourseSupervisor.objects.filter(course=obj).count()

    def get_member_count(self, obj):
        return UserCourse.objects.filter(course=obj).count()


class CourseCreateSerializer(serializers.ModelSerializer):
    # Khai báo tường minh để nhận list ID
    subjects = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    supervisors = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
    )
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Course
        fields = [
            "id",  # Thêm ID để frontend nhận được sau khi tạo
            "name",
            "link_to_course",
            "image",
            "start_date",
            "finish_date",
            "status",
            "subjects",
            "supervisors",
        ]

    def validate_subjects(self, value):
        # Lọc bỏ ID rỗng hoặc không hợp lệ nếu cần
        valid_ids = []
        for sid in value:
            if Subject.objects.filter(id=sid).exists():
                valid_ids.append(sid)
        return valid_ids

    def validate_supervisors(self, value):
        valid_ids = []
        for uid in value:
            if CustomUser.objects.filter(id=uid, role="SUPERVISOR").exists():
                valid_ids.append(uid)
        return valid_ids

    @transaction.atomic
    def create(self, validated_data):
        print("--- [DEBUG] SERIALIZER CREATE ---")

        # 1. TÁCH DỮ LIỆU M2M (QUAN TRỌNG)
        # pop() sẽ lấy dữ liệu ra và xóa khỏi validated_data
        # giúp tránh lỗi "unexpected keyword argument" khi tạo Course
        subjects_ids = validated_data.pop("subjects", [])
        supervisors_ids = validated_data.pop("supervisors", [])

        # 2. TẠO COURSE
        # creator được truyền vào từ perform_create của View thông qua save()
        course = Course.objects.create(**validated_data)

        # 3. TẠO SUPERVISORS (M2M)
        if supervisors_ids:
            links = [
                CourseSupervisor(course=course, supervisor_id=uid)
                for uid in supervisors_ids
            ]
            CourseSupervisor.objects.bulk_create(links)

        # 4. TẠO SUBJECTS & CLONE TASKS
        if subjects_ids:
            for idx, sub_id in enumerate(subjects_ids):
                # Tạo liên kết Course - Subject
                cs = CourseSubject.objects.create(
                    course=course, subject_id=sub_id, position=idx
                )

                # Lấy Tasks mẫu từ Subject gốc
                original_tasks = Task.objects.filter(
                    taskable_type=Task.TaskType.SUBJECT, taskable_id=sub_id
                )

                # Clone sang CourseSubject mới
                new_tasks = [
                    Task(
                        name=t.name,
                        taskable_type=Task.TaskType.COURSE_SUBJECT,
                        taskable_id=cs.id,
                        position=t.position,
                    )
                    for t in original_tasks
                ]
                Task.objects.bulk_create(new_tasks)

        return course


class UserCourseMemberSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = UserCourse
        fields = ["id", "user_name", "status", "joined_at"]
