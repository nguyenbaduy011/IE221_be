from django.db import models

class Courses(models.Model):
    # Enum cho trạng thái của khóa học
    class Status(models.IntegerChoices):
        NOT_STARTED = 0, 'Not Started'   # 0 = chưa bắt đầu
        IN_PROGRESS = 1, 'In Progress'   # 1 = đang học
        FINISHED = 2, 'Finished'         # 2 = đã hoàn thành

    # Tên khóa học
    name = models.CharField(max_length=100)

    # Ngày bắt đầu khóa học
    start_date = models.DateField()

    # Ngày kết thúc khóa học
    finish_date = models.DateField()

    # ID người tạo khóa học
    creator_id = models.BigIntegerField()

    # Trạng thái khóa học
    status = models.IntegerField(choices=Status.choices, default=Status.NOT_STARTED)

    # Thời điểm tạo bản ghi
    created_at = models.DateTimeField(auto_now_add=True)

    # Thời điểm cập nhật bản ghi
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.name
