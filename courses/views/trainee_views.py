from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from courses.models.course_model import Course
from courses.models.course_supervisor_model import CourseSupervisor
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from courses.serializers.course_serializer import CourseSerializer
from courses.serializers.course_supervisor_serializer import CourseSupervisorSerializer, UserBasicSerializer
from courses.serializers.course_serializer import UserCourseMemberSerializer
from courses.selectors import get_all_courses, get_course_by_id

class TraineeCourseDetailView(APIView):
    permissions_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id):
        user_id = request.user
        # 1. Lấy Course
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found"}, status=404)

        # 2. Lấy UserCourse để xác định user có tham gia course không
        try:
            user_course = UserCourse.objects.get(user_id=user_id, course_id=course_id)
        except UserCourse.DoesNotExist:
            return Response({"detail": "User is not enrolled in this course"}, status=404)

        # 3. Lấy toàn bộ CourseSubject trong khóa học
        course_subjects = CourseSubject.objects.filter(course_id=course_id).order_by("position")

        result_subjects = []

        for cs in course_subjects:
            # 4. Tìm UserSubject tương ứng
            try:
                user_subject = UserSubject.objects.get(
                    user_id=user_id,
                    course_subject_id=cs.id,
                    user_course_id=user_course.id
                )
            except UserSubject.DoesNotExist:
                user_subject = None

            # 5. Build dữ liệu trả về
            result_subjects.append({
                "course_subject_id": cs.id,
                "position": cs.position,
                "start_date": cs.start_date,
                "finish_date": cs.finish_date,

                "subject": {
                    "id": cs.subject.id,
                    "name": cs.subject.name,
                    "max_score": cs.subject.max_score,
                    "estimated_time_days": cs.subject.estimated_time_days,
                    "image": request.build_absolute_uri(cs.subject.image.url) if cs.subject.image else None,
                },

                "progress": {
                    "status": user_subject.get_status_display() if user_subject else None,
                    "score": user_subject.score if user_subject else None,
                    "started_at": user_subject.started_at if user_subject else None,
                    "completed_at": user_subject.completed_at if user_subject else None,
                }
            })

        return Response({
            "course": CourseSerializer(course).data,
            "user_course_id": user_course.id,
            "subjects": result_subjects
        }, status=status.HTTP_200_OK)

class CourseMembersView(APIView):
    permissions_classes = [permissions.IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = get_course_by_id(course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)
    
        course_supervisors = CourseSupervisor.objects.filter(course=course).select_related('supervisor')

        list_of_supervisors = [link.supervisor for link in course_supervisors]

        supervisors_serializer = UserBasicSerializer(list_of_supervisors, many=True)
        user_courses = UserCourse.objects.filter(course=course) 
        serializer = UserCourseMemberSerializer(user_courses, many=True) 

        return Response({"course": CourseSerializer(course).data,
                        "members": serializer.data, 
                        "supervisors": supervisors_serializer.data, 
                        "member_count": user_courses.count(),
                        "supervisor_count": course_supervisors.count()
                        }, status=status.HTTP_200_OK)