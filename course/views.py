from rest_framework import generics
from .serializers import CourseSerializer
from . import selectors

class CourseListView(generics.ListAPIView):
    queryset = selectors.get_all_courses()
    serializer_class = CourseSerializer