from rest_framework import serializers
from authen.models import CustomUser
from courses.models.course_supervisor_model import CourseSupervisor
from courses.models.course_model import Course
from subjects.models.subject import Subject


class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ["id", "full_name"]


class CourseSupervisorSerializer(serializers.ModelSerializer):
    supervisor = UserBasicSerializer(read_only=True)

    class Meta:
        model = CourseSupervisor
        fields = ["id", "course", "supervisor", "created_at"]


class CourseCreateSerializer(serializers.ModelSerializer):
    # Field này nhận vào list các ID của User (ví dụ: [1, 2, 5])
    # write_only=True: Chỉ dùng khi tạo, không hiện ra khi get chi tiết (để tránh lặp data)
    supervisor_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=CustomUser.objects.filter(
            role="SUPERVISOR"
        ),  # Chỉ cho phép chọn user có role Supervisor (tùy logic)
        source="supervisors",  # Mapping field này vào logic xử lý
        write_only=True,
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
            "supervisor_ids",  # Field nhận input
        ]
        read_only_fields = ["creator", "status", "created_at"]

    def validate_supervisor_ids(self, value):
        """Kiểm tra xem có ít nhất 1 supervisor được gửi lên không"""
        if not value or len(value) == 0:
            raise serializers.ValidationError(
                "Course must have at least one supervisor."
            )
        return value

    def create(self, validated_data):
        # 1. Tách danh sách supervisors ra khỏi data tạo course
        supervisors = validated_data.pop("supervisors", [])

        # 2. Sử dụng transaction để đảm bảo toàn vẹn dữ liệu (Create Course + Create Links)
        with transaction.atomic():
            # Tạo Course trước
            course = Course.objects.create(**validated_data)

            # Tạo các liên kết trong bảng trung gian CourseSupervisor
            course_supervisor_links = [
                CourseSupervisor(course=course, supervisor=user) for user in supervisors
            ]

            # Bulk create để tối ưu performance (chỉ 1 câu query insert nhiều dòng)
            CourseSupervisor.objects.bulk_create(course_supervisor_links)

        return course


class AddSubjectTaskSerializer(serializers.Serializer):
    # Nếu chọn subject có sẵn
    subject_id = serializers.IntegerField(required=False, allow_null=True)

    # Nếu tạo subject mới
    name = serializers.CharField(required=False, max_length=100)
    max_score = serializers.IntegerField(required=False)
    estimated_time_days = serializers.IntegerField(required=False)
    image = serializers.ImageField(required=False)

    # Danh sách tên các task (VD: ["Task 1", "Task 2"])
    tasks = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, default=list
    )

    def validate(self, data):
        subject_id = data.get("subject_id")

        if not subject_id:
            # Nếu không có ID => Đang tạo mới => Bắt buộc phải có thông tin Subject
            if not data.get("name"):
                raise serializers.ValidationError(
                    "Name is required when creating a new subject."
                )
            if not data.get("max_score"):
                raise serializers.ValidationError(
                    "Max score is required for new subject."
                )
            if not data.get("estimated_time_days"):
                raise serializers.ValidationError(
                    "Estimated time is required for new subject."
                )
        else:
            # Nếu có ID => Check xem subject đó tồn tại không
            if not Subject.objects.filter(id=subject_id).exists():
                raise serializers.ValidationError("Subject ID does not exist.")

        return data


class AddTraineeSerializer(serializers.Serializer):
    trainee_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.filter(role="TRAINEE")
    )

    def validate_trainee_ids(self, value):
        try:
            trainee = CustomUser.objects.get(id=value.id)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                f"Trainee with ID {value.id} does not exist."
            )

        if trainee.role != CustomUser.Role.TRAINEE:
            raise serializers.ValidationError(
                f"User with ID {value.id} is not a trainee."
            )

        return value
