from rest_framework import serializers
from courses.models.course_model import Course
from courses.models.course_supervisor_model import CourseSupervisor
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from courses.models.course_subject import CourseSubject
from authen.models import CustomUser


class TrainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email']

class TraineeMemberSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    joined_at = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'status', 'joined_at']

    def get_status(self, obj):
        user_course_map = self.context.get('user_course_map', {})
        uc = user_course_map.get(obj.id)
        if uc:
            return uc.get_status_display()
        return "Unknown"

    def get_joined_at(self, obj):
        user_course_map = self.context.get('user_course_map', {})
        uc = user_course_map.get(obj.id)
        if uc and uc.joined_at:
            return uc.joined_at.strftime("%d/%m/%Y")
        return ""

class CourseSubjectInfoSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name')
    subject_image = serializers.ImageField(source='subject.image', read_only=True)
    max_score = serializers.IntegerField(source='subject.max_score')
    
    my_status = serializers.SerializerMethodField()
    my_score = serializers.SerializerMethodField()
    supervisor_comment = serializers.SerializerMethodField()
    supervisor_info = serializers.SerializerMethodField()
    comment_at = serializers.SerializerMethodField()

    class Meta:
        model = CourseSubject
        fields = [
            'id', 'subject_id', 'subject_name', 'subject_image', 'max_score', 
            'start_date', 'finish_date', 
            'my_status', 'my_score', 'supervisor_comment', 'supervisor_info', 'comment_at'
        ]

    def _get_user_subject(self, obj):
        user_subjects = self.context.get('user_subjects_map', {})
        return user_subjects.get(obj.id)

    def get_my_status(self, obj):
        us = self._get_user_subject(obj)
        return us.get_status_display() if us else "Not Started"

    def get_my_score(self, obj):
        us = self._get_user_subject(obj)
        return us.score if us else None

    def get_supervisor_comment(self, obj):
        return "" 

    def get_supervisor_info(self, obj):
        return None 
    
    def get_comment_at(self, obj):
        return None


class TraineeCourseFullDetailSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='creator.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    updated_at_fmt = serializers.SerializerMethodField()
    start_date_fmt = serializers.SerializerMethodField()
    finish_date_fmt = serializers.SerializerMethodField()
    
    subjects = serializers.SerializerMethodField()
    members = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'name', 'image', 'status', 'status_display', 
            'start_date_fmt', 'finish_date_fmt', 'creator_name', 'updated_at_fmt',
            'subjects', 'members'
        ]

    def get_updated_at_fmt(self, obj):
        return obj.updated_at.strftime("%d/%m/%Y %H:%M:%S")

    def get_start_date_fmt(self, obj):
        return obj.start_date.strftime("%d/%m/%Y")

    def get_finish_date_fmt(self, obj):
        return obj.finish_date.strftime("%d/%m/%Y")

    def get_subjects(self, obj):
        qs = CourseSubject.objects.filter(course=obj).select_related('subject').order_by('position')
        
        request = self.context.get('request')
        user_subjects_map = {}
        if request:
            user_subjects = UserSubject.objects.filter(
                user=request.user, 
                course_subject__course=obj
            )
            user_subjects_map = {us.course_subject_id: us for us in user_subjects}

        return {
            "count": qs.count(),
            "list": CourseSubjectInfoSerializer(qs, many=True, context={'user_subjects_map': user_subjects_map}).data
        }

    def get_members(self, obj):
        supervisors = obj.supervisors.all().select_related('supervisor')
        trainer_list = [s.supervisor for s in supervisors]
        
        user_courses = UserCourse.objects.filter(course=obj).select_related('user')
        trainee_list = [uc.user for uc in user_courses]
        
        uc_map = {uc.user.id: uc for uc in user_courses}

        return {
            "trainers": {
                "count": len(trainer_list),
                "list": TrainerSerializer(trainer_list, many=True).data
            },
            "trainees": {
                "count": len(trainee_list),
                "list": TraineeMemberSerializer(trainee_list, many=True, context={'user_course_map': uc_map}).data
            }
        }