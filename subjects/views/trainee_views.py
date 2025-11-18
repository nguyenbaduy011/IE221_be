from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from subjects.serializers.subject_serializers import SubjectSerializer
from subjects.selectors import get_subject_by_id, search_subjects

class IsTrainee(permissions.BasePermission):
    def has_permission(self, request, view):
        # Cho phép trainee và cả các role khác truy cập view public search nếu cần
        # Hoặc strict chỉ trainee:
        return request.user.is_authenticated and getattr(request.user, 'role', None) == 'trainee'

class TraineeSubjectListView(APIView):
    """
    API Search/List Subject dành cho Trainee (Tương ứng resources :subjects, only: :index trong Rails)
    """
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated] # Có thể mở cho all authenticated users

    def get(self, request):
        query = request.query_params.get('query')
        subjects = search_subjects(query=query)
        serializer = self.serializer_class(subjects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TraineeSubjectDetailView(APIView):
    """
    Xem chi tiết Subject (Tương ứng Trainee::SubjectsController#show)
    """
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsTrainee]

    def get(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)

        # Logic ensure_user_enrollments (như file Ruby) nên được gọi ở đây
        # ví dụ: ensure_trainee_enrollment(request.user, subject)

        serializer = self.serializer_class(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)