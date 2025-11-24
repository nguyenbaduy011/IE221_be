from rest_framework import serializers
from courses.models.course_model import Course
from courses.models.course_subject import CourseSubject
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject 

class TraineeCourseListSerializer(serializers.ModelSerializer):
    supervisors = serializers.SerializerMethodField()
    subject_count = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',            
            'name',          
            'image',
            'start_date',   
            'status',        
            'supervisors',  
            'progress',     
            'subject_count', 
            'member_count',  
        ]

    def get_supervisors(self, obj):

        return [
            cs.supervisor.full_name 
            for cs in obj.supervisors.all() 
            if cs.supervisor
        ]

    def get_subject_count(self, obj):
        return CourseSubject.objects.filter(course=obj).count()

    def get_member_count(self, obj):

        return UserCourse.objects.filter(course=obj).count()

    def get_progress(self, obj):

        request = self.context.get('request')
        if not request or not request.user:
            return 0.0

        total_subjects = CourseSubject.objects.filter(course=obj).count()
        if total_subjects == 0:
            return 0.0

        completed_subjects = UserSubject.objects.filter(
            user=request.user,
            course_subject__course=obj,
            status=2 
        ).count()

        return round((completed_subjects / total_subjects) * 100, 1)