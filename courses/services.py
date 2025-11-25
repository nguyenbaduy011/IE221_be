from courses.models.course_model import Course
from courses.models.course_subject import CourseSubject
from courses.models.course_supervisor_model import CourseSupervisor


class CourseCreateService:
    @staticmethod
    def create_course(user, validated_data):
        subjects = validated_data.pop('subjects', [])
        supervisors = validated_data.pop('supervisors', [])

        if len(subjects) < 1:
            raise ValueError("A course must have at least one subject.")
        
        course = Course.objects.create(creator=user, **validated_data)

        if not supervisors:
            supervisors = [user.id]

        for supervisor_id in supervisors:
            CourseSupervisor.objects.create(
                course=course,
                supervisor_id=supervisor_id
            )

        for idx, subject_id in enumerate(subjects):
            CourseSubject.objects.create(
                course=course,
                subject_id=subject_id,
                position=idx
            )

        return course