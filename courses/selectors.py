from courses.models.course_model import Course

# Lấy tất cả các khóa học
def get_all_courses() -> list[Course]:
    return Course.objects.all()

# Lấy khóa học theo ID
def get_course_by_id(course_id) -> Course | None:
    try:
        return Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return None

# Lấy khóa học theo tên, người tạo
def get_courses_by_name_and_creator(name: str, creator_id: int) -> list[Course]:
    queryset = Course.objects.all()

    if name:
        queryset = queryset.filter(name__icontains=name)
    if creator_id:
        queryset = queryset.filter(creator_id=creator_id)

    return queryset
