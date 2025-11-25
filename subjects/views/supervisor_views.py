from rest_framework import status, permissions, filters, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction
from users.models.user_subject import UserSubject

from users.models.user_task import UserTask
from courses.models.course_subject import CourseSubject
from subjects.models.task import Task
from subjects.models.category import Category  # Import Category

from subjects.serializers.subject_serializers import SubjectSerializer
from subjects.serializers.task_serializers import TaskSerializer
from subjects.serializers.category_serializers import (
    CategorySerializer,
)

from subjects.selectors import (
    get_subject_by_id,
    search_subjects,
    search_categories,
    get_category_by_id,
)
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from authen.permissions import IsSupervisorRole, IsAdminOrSupervisor, IsTaskEditor
from subjects.models.subject import Subject


class SupervisorSubjectListView(APIView):
    """
    GET: Lấy danh sách hoặc tìm kiếm Subject
    POST: Tạo mới Subject
    """

    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        query = request.query_params.get("query")
        exclude_ids_raw = request.query_params.get("exclude_ids")

        exclude_ids = []
        if exclude_ids_raw:
            try:
                exclude_ids = [int(x) for x in exclude_ids_raw.split(",")]
            except ValueError:
                pass

        subjects = search_subjects(query=query, exclude_ids=exclude_ids)
        serializer = self.serializer_class(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SupervisorSubjectDetailView(APIView):
    """
    GET: Xem chi tiết
    PUT: Cập nhật
    DELETE: Xóa Subject và Tasks liên quan
    """

    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response(
                {"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response(
                {"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.serializer_class(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response(
                {"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if CourseSubject.objects.filter(subject_id=subject.id).exists():
            return Response(
                {
                    "detail": "Không thể xóa môn học này vì đang thuộc về ít nhất một khóa học."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                Task.objects.filter(
                    taskable_type=Task.TaskType.SUBJECT, taskable_id=subject.id
                ).delete()

                subject.delete()

        except Exception as e:
            return Response(
                {"detail": f"Lỗi hệ thống khi xóa: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskViewSet(viewsets.ModelViewSet):
    """
    CRUD Task.
    - Permission:
        + GET: All Authenticated Users (Admin, Supervisor, Trainee).
        + POST/PUT/DELETE: Admin OR Supervisor of the related Course.
    """

    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get_queryset(self):
        """
        Lọc Task:
        - Nếu có param 'subject_id', trả về tasks của subject đó.
        - Nếu có param 'search', tìm theo tên.
        """
        queryset = Task.objects.all()

        # Filter by subject_id
        subject_id = self.request.query_params.get("subject_id")
        if subject_id:
            # Lấy Task thuộc Subject gốc HOẶC Task thuộc các CourseSubject liên quan
            course_subject_ids = CourseSubject.objects.filter(
                subject_id=subject_id
            ).values_list("id", flat=True)

            queryset = queryset.filter(
                Q(taskable_type=Task.TaskType.SUBJECT, taskable_id=subject_id)
                | Q(
                    taskable_type=Task.TaskType.COURSE_SUBJECT,
                    taskable_id__in=course_subject_ids,
                )
            )

        # Search by name
        search_query = self.request.query_params.get("search")
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)

        return queryset.order_by("-created_at")

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Tạo Task và tự động assign cho tất cả học viên đang học Subject đó.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 1. Tạo Task gốc
        task = serializer.save()

        # 2. Logic "Thêm task đối với tất cả học viên"
        if task.taskable_type == Task.TaskType.SUBJECT:
            subject_id = task.taskable_id

            # Lấy tất cả UserSubject liên quan
            active_user_subjects = UserSubject.objects.filter(
                course_subject__subject_id=subject_id
            ).select_related(
                "user"
            )

            user_tasks_to_create = []
            processed_user_ids = set()  # Dùng set để theo dõi các user đã xử lý

            for user_subject in active_user_subjects:
                user_id = user_subject.user.id

                # BƯỚC QUAN TRỌNG: Kiểm tra trùng lặp trong danh sách đang xử lý
                # Nếu user này đã được thêm vào list rồi thì bỏ qua bản ghi UserSubject thứ 2
                if user_id in processed_user_ids:
                    continue

                # Kiểm tra trong DB (đề phòng trường hợp task cũ assign lại)
                if not UserTask.objects.filter(user_id=user_id, task=task).exists():
                    user_tasks_to_create.append(
                        UserTask(
                            user=user_subject.user,
                            task=task,
                            user_subject=user_subject,
                            status=UserTask.Status.NOT_DONE,
                        )
                    )
                    # Đánh dấu đã xử lý user này
                    processed_user_ids.add(user_id)

            # Bulk create với ignore_conflicts=True (trên Postgres) để an toàn tuyệt đối
            if user_tasks_to_create:
                UserTask.objects.bulk_create(
                    user_tasks_to_create, ignore_conflicts=True
                )

        return Response(
            {
                "message": "Create task success and assigned to trainees.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({"message": "Update task success", "data": serializer.data})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Khi xóa Task gốc, Django cascade sẽ tự động xóa UserTask liên quan
        # (do on_delete=models.CASCADE trong UserTask model)
        self.perform_destroy(instance)
        return Response(
            {"message": "Task deleted successfully"}, status=status.HTTP_204_NO_CONTENT
        )


# --- SUPERVISOR CATEGORY VIEWSET ---


class SupervisorCategoryViewSet(viewsets.ModelViewSet):
    """
    CRUD Category cho Supervisor.
    """

    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]

    def get_queryset(self):
        search_query = self.request.query_params.get("search")
        return search_categories(query=search_query)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {"message": "Create category success", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {"message": "Update category success", "data": serializer.data}
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Category deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )


class SubjectListView(generics.ListAPIView):
    """
    API: GET /api/subjects/?search=...
    """

    queryset = Subject.objects.all().order_by("name")
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    # Cấu hình tìm kiếm
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]
