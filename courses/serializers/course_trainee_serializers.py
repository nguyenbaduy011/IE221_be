from rest_framework import serializers
from courses.models.course_model import Course
from courses.models.course_subject import CourseSubject
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject  # Đảm bảo đã import model này

class TraineeCourseListSerializer(serializers.ModelSerializer):
    # Các trường tính toán custom
    supervisors = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',            # Dùng để redirect về màn hình SubjectList
            'name',          # Tên course
            'image',
            'start_date',    # Ngày bắt đầu
            'status',        # Status của course (0: Not Started, 1: In Progress, 2: Finished)
            'supervisors',   # Tên supervisor
            'progress',      # Tiến độ hoàn thành (%)
            'subject_count', # Số lượng subject
            'member_count',  # Số lượng học viên
        ]

    def get_supervisors(self, obj):
        """
        Lấy danh sách tên Supervisor.
        Dựa trên related_name='supervisors' trong model CourseSupervisor
        """
        # obj.supervisors là QuerySet các đối tượng CourseSupervisor
        return [
            cs.supervisor.full_name 
            for cs in obj.supervisors.all() 
            if cs.supervisor
        ]

    def get_subject_count(self, obj):
        """Đếm tổng số môn học trong khóa."""
        return CourseSubject.objects.filter(course=obj).count()

    def get_member_count(self, obj):
        """
        Đếm tổng số học viên (UserCourse) tham gia khóa học.
        Dựa trên model UserCourse
        """
        return UserCourse.objects.filter(course=obj).count()

    def get_progress(self, obj):
        """
        Tính % hoàn thành = (Số môn đã hoàn thành / Tổng số môn) * 100
        """
        request = self.context.get('request')
        if not request or not request.user:
            return 0.0

        total_subjects = CourseSubject.objects.filter(course=obj).count()
        if total_subjects == 0:
            return 0.0

        # Đếm số môn user đã hoàn thành (Dựa vào UserSubject status)
        # Giả định status=2 là hoàn thành (tương tự UserCourse.Status.FINISH)
        # Bạn cần thay số 2 bằng UserSubject.Status.FINISH nếu có class Choices
        completed_subjects = UserSubject.objects.filter(
            user=request.user,
            course_subject__course=obj,
            status=2 
        ).count()

        return round((completed_subjects / total_subjects) * 100, 1)