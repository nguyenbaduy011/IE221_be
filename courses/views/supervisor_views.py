from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from authen.permissions import IsAdminOrSupervisor
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from courses.models.course_model import Course
from courses.models.course_subject import CourseSubject
from subjects.models.subject import Subject
from django.contrib.contenttypes.models import ContentType
from users.models.comment import Comment
from subjects.models.task import Task
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from users.models.user_task import UserTask
from django.shortcuts import get_object_or_404
from django.db import transaction
from courses.serializers.course_supervisor_serializer import *
from courses.selectors import get_all_courses, get_course_by_id
from courses.serializers.course_serializer import CourseSerializer, CourseCreateSerializer

class SupervisorCourseListView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        courses = get_all_courses().order_by("-created_at")
        serializer = self.serializer_class(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupervisorMyCourseListView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        user = self.request.user
        course = (
            Course.objects.filter(course_supervisors=user)
            .distinct()
            .order_by("-created_at")
        )
        return Response(
            self.serializer_class(course, many=True).data, status=status.HTTP_200_OK
        )


class SupervisorCourseDetailView(APIView):
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request, course_id):
        user = self.request.user
        course = get_course_by_id(course_id)
        if not course:
            return Response(
                {"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND
            )

        if (
            getattr(user, "role", None) != "ADMIN"
            and not course.course_supervisors.filter(supervisor=user).exists()
        ):
            return Response(
                {"detail": "You do not have permission to view this course."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.serializer_class(course)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupervisorCourseCreateView(APIView):
    serializer_class = CourseCreateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class AddSubjectToCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        serializer = AddSubjectTaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        subject_id = data.get("subject_id")
        task_names = data.get("tasks", [])

        try:
            with transaction.atomic():
                if subject_id:
                    subject = Subject.objects.get(pk=subject_id)

                    course_subject = CourseSubject.objects.create(
                        course=course,
                        subject=subject,
                    )


                    template_tasks = Task.objects.filter(
                        taskable_type=Task.TaskType.SUBJECT, taskable_id=subject.id
                    )

                    new_tasks = []
                    for template in template_tasks:
                        new_tasks.append(
                            Task(
                                name=template.name,
                                taskable_type=Task.TaskType.COURSE_SUBJECT,
                                taskable_id=course_subject.id,
                            )
                        )

                    for name in task_names:
                        new_tasks.append(
                            Task(
                                name=name,
                                taskable_type=Task.TaskType.COURSE_SUBJECT,
                                taskable_id=course_subject.id,
                            )
                        )

                    Task.objects.bulk_create(new_tasks)

                    message = "Added existing subject and cloned tasks successfully."

                else:
                    subject = Subject.objects.create(
                        name=data["name"],
                        max_score=data["max_score"],
                        estimated_time_days=data["estimated_time_days"],
                        image=data.get("image"),
                    )

                    new_tasks = []
                    for name in task_names:
                        new_tasks.append(
                            Task(
                                name=name,
                                taskable_type=Task.TaskType.SUBJECT,
                                taskable_id=subject.id,
                            )
                        )
                    Task.objects.bulk_create(new_tasks)
                    CourseSubject.objects.create(course=course, subject=subject)

                    message = "Created new subject and template tasks successfully."

                return Response(
                    {"message": message, "subject_id": subject.id},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AddTraineeToCourseView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsAdminOrSupervisor,
    ]  

    def post(self, request, course_id):
        course = get_object_or_404(Course, pk=course_id)

        serializer = AddTraineeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        trainees = serializer.validated_data["trainee_ids"]

        course_subjects = list(CourseSubject.objects.filter(course=course))

        tasks_map = {}

        cs_ids = [cs.id for cs in course_subjects]
        relevant_tasks = Task.objects.filter(
            taskable_type=Task.TaskType.COURSE_SUBJECT, taskable_id__in=cs_ids
        )

        for task in relevant_tasks:
            if task.taskable_id not in tasks_map:
                tasks_map[task.taskable_id] = []
            tasks_map[task.taskable_id].append(task)

        added_count = 0
        skipped_count = 0
        all_user_tasks_to_create = (
            []
        ) 

        try:
            with transaction.atomic():
                for trainee in trainees:
                    if UserCourse.objects.filter(user=trainee, course=course).exists():
                        skipped_count += 1
                        continue
                    user_course = UserCourse.objects.create(
                        user=trainee,
                        course=course,
                        status=UserCourse.Status.NOT_STARTED,
                    )
                    for cs in course_subjects:
                        user_subject = UserSubject.objects.create(
                            user=trainee,
                            user_course=user_course,
                            course_subject=cs,
                            status=UserSubject.Status.NOT_STARTED,
                        )

                        tasks_of_cs = tasks_map.get(cs.id, [])

                        for task in tasks_of_cs:
                            all_user_tasks_to_create.append(
                                UserTask(
                                    user=trainee,
                                    task=task,
                                    user_subject=user_subject,
                                    status=UserTask.Status.NOT_DONE,
                                )
                            )

                    added_count += 1

                if all_user_tasks_to_create:
                    UserTask.objects.bulk_create(all_user_tasks_to_create)

            return Response(
                {
                    "message": "Process completed.",
                    "added": added_count,
                    "skipped": skipped_count,
                    "detail": f"Successfully added {added_count} trainees to course '{course.name}'.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CourseManagementViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]
    @action(detail=True, methods=["post"], url_path="add-supervisors")
    def add_supervisors(self, request, pk=None):
        course = self.get_object()
        serializer = AddSupervisorSerializer(data=request.data)
        if serializer.is_valid():
            supervisor_ids = serializer.validated_data["supervisor_ids"]

            existing_ids = CourseSupervisor.objects.filter(
                course=course, supervisor__in=supervisor_ids
            ).values_list("supervisor_id", flat=True)

            new_links = [
                CourseSupervisor(course=course, supervisor=sup)
                for sup in supervisor_ids
                if sup.id not in existing_ids
            ]

            CourseSupervisor.objects.bulk_create(new_links)
            return Response(
                {"message": f"Added {len(new_links)} supervisors."},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["delete"], url_path="remove-supervisor")
    def remove_supervisor(self, request, pk=None):
        course = self.get_object()
        serializer = DeleteIDSerializer(data=request.data)
        if serializer.is_valid():
            supervisor_id = serializer.validated_data["id"]
            deleted, _ = CourseSupervisor.objects.filter(
                course=course, supervisor_id=supervisor_id
            ).delete()

            if deleted:
                return Response(
                    {"message": "Supervisor removed."}, status=status.HTTP_200_OK
                )
            return Response(
                {"message": "Supervisor not found in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], url_path="add-trainees")
    def add_trainees(self, request, course_id=None):
        course = get_object_or_404(Course, pk=course_id)

        serializer = AddTraineeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        trainees = serializer.validated_data["trainee_ids"]

        course_subjects = list(CourseSubject.objects.filter(course=course))

        tasks_map = {}

        cs_ids = [cs.id for cs in course_subjects]
        relevant_tasks = Task.objects.filter(
            taskable_type=Task.TaskType.COURSE_SUBJECT, taskable_id__in=cs_ids
        )
        for task in relevant_tasks:
            if task.taskable_id not in tasks_map:
                tasks_map[task.taskable_id] = []
            tasks_map[task.taskable_id].append(task)


        added_count = 0
        skipped_count = 0
        all_user_tasks_to_create = (
            []
        )  

        try:
            with transaction.atomic():
                for trainee in trainees:
                    if UserCourse.objects.filter(user=trainee, course=course).exists():
                        skipped_count += 1
                        continue

                    user_course = UserCourse.objects.create(
                        user=trainee,
                        course=course,
                        status=UserCourse.Status.NOT_STARTED,
                    )

                    for cs in course_subjects:
                        user_subject = UserSubject.objects.create(
                            user=trainee,
                            user_course=user_course,
                            course_subject=cs,
                            status=UserSubject.Status.NOT_STARTED,
                        )

                        tasks_of_cs = tasks_map.get(cs.id, [])

                        for task in tasks_of_cs:
                            all_user_tasks_to_create.append(
                                UserTask(
                                    user=trainee,
                                    task=task,
                                    user_subject=user_subject,
                                    status=UserTask.Status.NOT_DONE,
                                )
                            )

                    added_count += 1

                if all_user_tasks_to_create:
                    UserTask.objects.bulk_create(all_user_tasks_to_create)

            return Response(
                {
                    "message": "Process completed.",
                    "added": added_count,
                    "skipped": skipped_count,
                    "detail": f"Successfully added {added_count} trainees to course '{course.name}'.",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["delete"], url_path="remove-trainee")
    def remove_trainee(self, request, pk=None):
        course = self.get_object()
        serializer = DeleteIDSerializer(data=request.data)
        if serializer.is_valid():
            trainee_id = serializer.validated_data["id"]

            deleted, _ = UserCourse.objects.filter(
                course=course, user_id=trainee_id
            ).delete()

            if deleted:
                return Response(
                    {"message": "Trainee removed and all data cleaned."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Trainee not found in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=["post"], url_path="add-subject")
    def add_subject(self, request, pk=None):
        course = self.get_object()

        serializer = AddSubjectTaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        subject_id = data.get("subject_id")
        task_names = data.get("tasks", [])

        try:
            with transaction.atomic():
                final_tasks_for_user = []

                if subject_id:
                    subject = Subject.objects.get(pk=subject_id)

                    course_subject = CourseSubject.objects.create(
                        course=course,
                        subject=subject,
                    )

                    template_tasks = Task.objects.filter(
                        taskable_type=Task.TaskType.SUBJECT, taskable_id=subject.id
                    )

                    new_tasks = []
                    for template in template_tasks:
                        new_tasks.append(
                            Task(
                                name=template.name,
                                taskable_type=Task.TaskType.COURSE_SUBJECT,  
                                taskable_id=course_subject.id,
                            )
                        )
                    for name in task_names:
                        new_tasks.append(
                            Task(
                                name=name,
                                taskable_type=Task.TaskType.COURSE_SUBJECT,  
                                taskable_id=course_subject.id,
                            )
                        )
                    created_tasks = Task.objects.bulk_create(new_tasks)
                    final_tasks_for_user = created_tasks
                    message = "Added existing subject and cloned tasks successfully."
                else:
                    subject = Subject.objects.create(
                        name=data["name"],
                        max_score=data["max_score"],
                        estimated_time_days=data["estimated_time_days"],
                        image=data.get("image"),
                    )

                    new_tasks = []
                    for name in task_names:
                        new_tasks.append(
                            Task(
                                name=name,
                                taskable_type=Task.TaskType.SUBJECT,  
                                taskable_id=subject.id,
                            )
                        )

                    created_tasks = Task.objects.bulk_create(new_tasks)

                    course_subject = CourseSubject.objects.create(
                        course=course, subject=subject
                    )

                    final_tasks_for_user = created_tasks
                    message = "Created new subject and template tasks successfully."

                existing_user_courses = UserCourse.objects.filter(course=course)

                if existing_user_courses.exists():
                    new_user_subjects = []
                    new_user_tasks = []

                    for uc in existing_user_courses:

                        user_subject = UserSubject.objects.create(
                            user=uc.user,
                            user_course=uc,
                            course_subject=course_subject,
                            status=UserSubject.Status.NOT_STARTED,
                        )

                        for task in final_tasks_for_user:
                            new_user_tasks.append(
                                UserTask(
                                    user=uc.user,
                                    task=task,
                                    user_subject=user_subject,
                                    status=UserTask.Status.NOT_DONE,
                                )
                            )

                    if new_user_tasks:
                        UserTask.objects.bulk_create(new_user_tasks)

                return Response(
                    {"message": message, "subject_id": subject.id},
                    status=status.HTTP_201_CREATED,
                )

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=["delete"], url_path="remove-subject")
    def remove_subject(self, request, pk=None):
        course = self.get_object()
        serializer = DeleteIDSerializer(data=request.data)

        if serializer.is_valid():
            cs_id = serializer.validated_data["id"]

            deleted, _ = CourseSubject.objects.filter(id=cs_id, course=course).delete()

            if deleted:
                return Response(
                    {"message": "Subject removed from course."},
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"message": "Subject not found in this course."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class SupervisorDashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request):
        user = request.user
        my_courses = Course.objects.filter(course_supervisors=user)

        active_courses_count = my_courses.filter(status=Course.Status.IN_PROGRESS).count()
        upcoming_count = my_courses.filter(status=Course.Status.NOT_STARTED).count()
        finished_count = my_courses.filter(status=Course.Status.FINISHED).count()

        total_trainees = UserCourse.objects.filter(course__in=my_courses).values('user').distinct().count()

        related_user_subjects = UserSubject.objects.filter(user_course__course__in=my_courses)
        total_subjects_taken = related_user_subjects.count()
        finished_subjects = related_user_subjects.filter(
            status__in=[
                UserSubject.Status.FINISHED_EARLY,
                UserSubject.Status.FINISHED_ON_TIME,
                UserSubject.Status.FINISED_BUT_OVERDUE, 
            ]
        ).count() if total_subjects_taken > 0 else 0
        completion_rate = round((finished_subjects / total_subjects_taken) * 100, 2) if total_subjects_taken else 0.0

        chart_data = [
            {"name": "Active", "value": active_courses_count, "color": "#3b82f6"},
            {"name": "Upcoming", "value": upcoming_count, "color": "#f59e0b"},
            {"name": "Completed", "value": finished_count, "color": "#10b981"},
        ]

        recent_joins = UserCourse.objects.filter(course__in=my_courses).select_related('user', 'course').order_by('-joined_at')[:5]
        activities = [
            {
                "id": item.id,
                "user": item.user.full_name or item.user.email,
                "action": "joined course",
                "target": item.course.name,
                "time": item.joined_at,
                "avatar": ""
            } for item in recent_joins
        ]

        return Response({
            "active_courses": active_courses_count,
            "total_trainees": total_trainees,
            "completion_rate": completion_rate,
            "chart_data": chart_data,
            "recent_activities": activities,
        }, status=status.HTTP_200_OK)

class SupervisorCourseStudentsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request, course_id):
        classmates = UserCourse.objects.filter(
            course_id=course_id
        ).select_related('user')

        data = []
        for item in classmates:
            avatar_url = None

            data.append({
                "id": item.user.id,
                "full_name": item.user.full_name,
                "email": item.user.email,
                "avatar": avatar_url
            })

        return Response({"data": data}, status=status.HTTP_200_OK)


class SupervisorUserSubjectDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def get(self, request, subject_id, student_id):
        user_subject = get_object_or_404(
            UserSubject, 
            course_subject_id=subject_id, 
            user_id=student_id
        )
        course_subject = user_subject.course_subject
        
        tasks_qs = UserTask.objects.filter(user_subject=user_subject).select_related('task')
        tasks_data = [{
            "id": t.id,
            "name": t.task.name if t.task else "Unnamed Task",
            "status": "DONE" if (t.status == 1 or t.status == "COMPLETED") else "NOT_DONE"
        } for t in tasks_qs]

        content_type = ContentType.objects.get_for_model(UserSubject)
        last_comment = Comment.objects.filter(
            content_type=content_type, 
            object_id=user_subject.id
        ).order_by('-updated_at').first()
        
        supervisor_comment = last_comment.content if last_comment else ""
        comment_updated_at = last_comment.updated_at if last_comment else None

        response_data = {
            "id": user_subject.id,
            "name": course_subject.subject.name,
            "course_name": course_subject.course.name,
            "supervisor_name": request.user.full_name,
            "last_updated": user_subject.updated_at,
            "duration": f"{course_subject.subject.estimated_time_days or 0} days",
            "start_date": course_subject.start_date,
            "end_date": course_subject.finish_date,
            "actual_start_date": user_subject.started_at,
            "actual_end_date": user_subject.completed_at,
            
            "score": user_subject.score,                 
            "max_score": course_subject.subject.max_score,
            "supervisor_comment": supervisor_comment,   
            "comment_updated_at": comment_updated_at,
            "status": "COMPLETED" if user_subject.status == 2 else "IN_PROGRESS",
            "tasks": tasks_data
        }

        return Response({"data": response_data}, status=status.HTTP_200_OK)

class SupervisorSubjectTaskCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def post(self, request, subject_id):
        course_subject = get_object_or_404(CourseSubject, pk=subject_id)
        name = request.data.get("name")

        if not name:
            return Response({"detail": "Task name is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                new_task = Task.objects.create(
                    name=name,
                    taskable_type=Task.TaskType.COURSE_SUBJECT,
                    taskable_id=course_subject.id,
                    position=0 
                )

                related_user_subjects = UserSubject.objects.filter(course_subject=course_subject)

                user_tasks = []
                for us in related_user_subjects:
                    user_tasks.append(
                        UserTask(
                            user=us.user,
                            task=new_task,
                            user_subject=us,
                            status=1 
                        )
                    )
                
                if user_tasks:
                    UserTask.objects.bulk_create(user_tasks)

                return Response({
                    "message": "Task added to subject and assigned to all students.",
                    "task_id": new_task.id
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SupervisorUserSubjectAssessmentView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def patch(self, request, pk):
        user_subject = get_object_or_404(UserSubject, pk=pk)
        
        score = request.data.get("score")
        comment_content = request.data.get("supervisor_comment")

        try:
            with transaction.atomic():
                if score is not None:
                    max_score = user_subject.course_subject.subject.max_score
                    if float(score) > max_score:
                        return Response({"detail": f"Score cannot exceed {max_score}"}, status=400)
                    user_subject.score = score
                    user_subject.save()

                if comment_content is not None:
                    content_type = ContentType.objects.get_for_model(UserSubject)
                    
                    existing_comments = Comment.objects.filter(
                        content_type=content_type,
                        object_id=user_subject.id,
                        user=request.user
                    )

                    if existing_comments.count() > 1:
                        latest_comment = existing_comments.order_by('-updated_at').first()
                        existing_comments.exclude(id=latest_comment.id).delete()
                    
                    Comment.objects.update_or_create(
                        content_type=content_type,
                        object_id=user_subject.id,
                        user=request.user,
                        defaults={'content': comment_content}
                    )

            return Response({"message": "Assessment updated successfully."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"ERROR SAVING ASSESSMENT: {str(e)}") 
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SupervisorTaskToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def patch(self, request, pk):
        user_task = get_object_or_404(UserTask, pk=pk)
        new_status_str = request.data.get("status")

        if new_status_str == "DONE":
            user_task.status = UserTask.Status.DONE 
        else:
            user_task.status = UserTask.Status.NOT_DONE
        
        user_task.save()
        return Response({"status": "success"}, status=status.HTTP_200_OK)


from django.utils import timezone

class SupervisorUserSubjectCompleteView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def post(self, request, pk):
        user_subject = get_object_or_404(UserSubject, pk=pk)

        try:
            with transaction.atomic():
                user_subject.status = 2 
                user_subject.completed_at = timezone.now()
                user_subject.save()

                UserTask.objects.filter(user_subject=user_subject).update(
                    status=UserTask.Status.COMPLETED 
                )

            return Response({"message": "Subject completed."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)