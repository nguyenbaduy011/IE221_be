from rest_framework import generics
from rest_framework.exceptions import NotFound
from .serializers import CourseSerializer
from . import selectors

class CourseListView(generics.ListAPIView):
    queryset = selectors.get_all_courses()
    serializer_class = CourseSerializer

from rest_framework import generics
from rest_framework.exceptions import NotFound
from .serializers import CourseSerializer
from . import selectors

class CourseListView(generics.ListAPIView):
    queryset = selectors.get_all_courses()
    serializer_class = CourseSerializer

class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseSerializer

    def get_object(self) -> object:
        # Lấy course_id từ query param
        course_id = self.request.query_params.get('id')

        if not course_id:
            raise NotFound("Missing 'id' parameter in request")

        course = selectors.get_course_by_id(course_id)
        if course is None:
            raise NotFound("Course not found")

        return course

class CourseSearchView(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self) -> list:
        name = self.request.query_params.get('name', '')
        creator_id = self.request.query_params.get('creator_id', None)

        if creator_id is not None:
            try:
                creator_id = int(creator_id)
            except ValueError:
                raise NotFound("Invalid 'creator_id' parameter")

        courses = selectors.get_courses_by_name_and_creator(name, creator_id)

        return courses