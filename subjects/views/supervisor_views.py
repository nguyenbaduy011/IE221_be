from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from subjects.models.task import Task
from subjects.serializers.subject_serializers import SubjectSerializer
from subjects.selectors import get_subject_by_id, search_subjects
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from authen.permissions import IsSupervisorRole, IsAdminOrSupervisor
from subjects.serializers.task_serializers import TaskSerializer
from subjects.models.subject import Subject

class SupervisorSubjectListView(APIView):
    """
    GET: Lấy danh sách hoặc tìm kiếm Subject
    POST: Tạo mới Subject
    """
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupervisorRole]

    def get(self, request):
        # Lấy params search giống file Ruby
        query = request.query_params.get('query')
        exclude_ids_raw = request.query_params.get('exclude_ids')
        
        exclude_ids = []
        if exclude_ids_raw:
            try:
                exclude_ids = [int(x) for x in exclude_ids_raw.split(',')]
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
    permission_classes = [permissions.IsAuthenticated, IsSupervisorRole]

    def get(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(subject, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Logic xóa tasks liên quan (giống destroy_tasks trong Rails)
        Task.objects.filter(taskable_type='subject', taskable_id=subject.id).delete()
        subject.delete()
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class SupervisorTaskViewSet(viewsets.ModelViewSet):
    """
    CRUD Task cho Supervisor.
    Endpoint: /api/v1/supervisor/tasks/
    """
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSupervisor]

    def get_queryset(self):
        """
        Lọc Task:
        1. Luôn luôn chỉ lấy task của Subject (taskable_type=0)
        2. Lọc theo subject_id nếu có param
        3. Tìm kiếm theo tên nếu có param search
        """
        # 1. Base scope: taskable_type = SUBJECT (0)
        queryset = Task.objects.filter(taskable_type=Task.TaskType.SUBJECT)

        # 2. Filter by subject_id (tương đương scope :by_subject trong Rails)
        subject_id = self.request.query_params.get('subject_id')
        if subject_id:
            queryset = queryset.filter(taskable_id=subject_id)

        # 3. Search by name (tương đương scope :search_by_name)
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
            
        return queryset.order_by('-created_at')

    # Các phương thức list, retrieve mặc định của ModelViewSet đã đủ dùng.
    # Dưới đây ta override create/update/destroy để trả về message format giống Rails flash message (tùy chọn).

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "message": "Create task success",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "message": "Update task success",
                "data": serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Task deleted successfully"}, 
            status=status.HTTP_204_NO_CONTENT
        )
    