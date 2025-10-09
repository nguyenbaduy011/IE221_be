from course.models import Courses

# Lấy tất cả các khóa học
def get_all_courses():
    return Courses.objects.all()