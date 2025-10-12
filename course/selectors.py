from course.models import Courses

# Lấy tất cả các khóa học
def get_all_courses() -> list[Courses]:
    return Courses.objects.all()

# Lấy khóa học theo ID
def get_course_by_id(course_id) -> Courses | None:
    try:
        return Courses.objects.get(id=course_id)
    except Courses.DoesNotExist:
        return None