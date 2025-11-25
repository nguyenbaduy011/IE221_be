from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from subjects.serializers.subject_serializers import SubjectSerializer
from subjects.selectors import get_subject_by_id, search_subjects
from authen.permissions import IsTraineeRole

class TraineeSubjectListView(APIView):
    """
    API Search/List Subject dành cho Trainee (Tương ứng resources :subjects, only: :index trong Rails)
    """
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    permission_classes = [permissions.IsAuthenticated, IsTraineeRole]

    def get(self, request, subject_id):
        subject = get_subject_by_id(subject_id)
        if not subject:
            return Response({"detail": "Subject not found."}, status=status.HTTP_404_NOT_FOUND)


        serializer = self.serializer_class(subject)
        return Response(serializer.data, status=status.HTTP_200_OK)
