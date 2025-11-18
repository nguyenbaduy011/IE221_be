from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from subjects.models.task import Task
from subjects.serializers.subject_serializers import SubjectSerializer
from subjects.selectors import get_subject_by_id, search_subjects

class IsSupervisor(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'role', None) in ['supervisor', 'admin']

class SupervisorSubjectListView(APIView):
    """
    GET: Lấy danh sách hoặc tìm kiếm Subject
    POST: Tạo mới Subject
    """
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsSupervisor]

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
    permission_classes = [permissions.IsAuthenticated, IsSupervisor]

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