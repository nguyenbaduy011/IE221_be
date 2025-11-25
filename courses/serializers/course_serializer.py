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


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["id", "name"]


class SubjectDetailSerializer(serializers.ModelSerializer):
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Subject
        fields = ["id", "name", "estimated_time_days", "image", "max_score", "tasks"]

    def get_tasks(self, obj):
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
            "id", 
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
        subjects_ids = validated_data.pop("subjects", [])
        supervisors_ids = validated_data.pop("supervisors", [])

        course = Course.objects.create(**validated_data)

        if supervisors_ids:
            links = [
                CourseSupervisor(course=course, supervisor_id=uid)
                for uid in supervisors_ids
            ]
            CourseSupervisor.objects.bulk_create(links)

        if subjects_ids:
            for idx, sub_id in enumerate(subjects_ids):
                cs = CourseSubject.objects.create(
                    course=course, subject_id=sub_id, position=idx
                )

                original_tasks = Task.objects.filter(
                    taskable_type=Task.TaskType.SUBJECT, taskable_id=sub_id
                )

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
