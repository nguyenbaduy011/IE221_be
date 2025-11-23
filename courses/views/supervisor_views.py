from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from authen.permissions import IsAdminOrSupervisor
from rest_framework.decorators import action
from rest_framework import viewsets

from courses.models.course_model import Course
from courses.models.course_subject import CourseSubject
from subjects.models.subject import Subject
from subjects.models.task import Task
from users.models.user_course import UserCourse
from users.models.user_subject import UserSubject
from users.models.user_task import UserTask
from django.shortcuts import get_object_or_404
from django.db import transaction
from courses.serializers.course_serializer import CourseSerializer
from courses.serializers.course_supervisor_serializer import *
from courses.selectors import get_all_courses, get_course_by_id


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
        # Tự động gán người tạo là User đang gửi request
        serializer.save(creator=self.request.user)


class AddSubjectToCourseView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    def post(self, request, course_id):
        # 1. Lấy Course
        course = get_object_or_404(Course, pk=course_id)

        # 2. Validate dữ liệu
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

                    # 1. Tạo liên kết Course - Subject
                    # position có thể tính toán tự động (lấy max position + 1)
                    course_subject = CourseSubject.objects.create(
                        course=course,
                        subject=subject,
                    )

                    # 2. Logic Task:

                    # Lấy các task mẫu của Subject
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

                    # Nếu user gửi thêm task mới trong request cho subject cũ này
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
                    # 1. Tạo Subject mới
                    subject = Subject.objects.create(
                        name=data["name"],
                        max_score=data["max_score"],
                        estimated_time_days=data["estimated_time_days"],
                        image=data.get("image"),
                    )

                    # 2. Logic Task:
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

                    # 3. Tạo liên kết CourseSubject
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
    ]  # Thêm permission phù hợp

    def post(self, request, course_id):
        # 1. Lấy Course
        course = get_object_or_404(Course, pk=course_id)

        # 2. Validate Input qua Serializer
        serializer = AddTraineeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Lấy danh sách User object từ serializer (nhờ PrimaryKeyRelatedField)
        trainees = serializer.validated_data["trainee_ids"]

        # ==================================================
        # BƯỚC CHUẨN BỊ DỮ LIỆU (TỐI ƯU PERFORMANCE)
        # ==================================================

        # Lấy tất cả CourseSubject của khóa học này 1 lần duy nhất
        course_subjects = list(CourseSubject.objects.filter(course=course))

        # Lấy tất cả Task của các CourseSubject đó 1 lần duy nhất
        # Map: { course_subject_id: [list_of_tasks] }
        tasks_map = {}

        # Lấy tất cả task có type là COURSE_SUBJECT và ID nằm trong list course_subjects
        cs_ids = [cs.id for cs in course_subjects]
        relevant_tasks = Task.objects.filter(
            taskable_type=Task.TaskType.COURSE_SUBJECT, taskable_id__in=cs_ids
        )

        # Gom nhóm task theo course_subject_id để dễ truy xuất
        for task in relevant_tasks:
            if task.taskable_id not in tasks_map:
                tasks_map[task.taskable_id] = []
            tasks_map[task.taskable_id].append(task)

        # ==================================================
        # BƯỚC XỬ LÝ GHI DỮ LIỆU (TRANSACTION)
        # ==================================================

        added_count = 0
        skipped_count = 0
        all_user_tasks_to_create = (
            []
        )  # List chứa tất cả UserTask để bulk_create cuối cùng

        try:
            with transaction.atomic():
                for trainee in trainees:
                    # Kiểm tra nếu trainee đã trong khóa học rồi thì bỏ qua
                    if UserCourse.objects.filter(user=trainee, course=course).exists():
                        skipped_count += 1
                        continue

                    # 1. Tạo UserCourse
                    user_course = UserCourse.objects.create(
                        user=trainee,
                        course=course,
                        status=UserCourse.Status.NOT_STARTED,
                    )

                    # 2. Tạo UserSubject & UserTask cho từng môn
                    for cs in course_subjects:
                        # Tạo UserSubject
                        user_subject = UserSubject.objects.create(
                            user=trainee,
                            user_course=user_course,
                            course_subject=cs,
                            status=UserSubject.Status.NOT_STARTED,
                        )

                        # Lấy các task thuộc môn học này từ Map đã chuẩn bị
                        tasks_of_cs = tasks_map.get(cs.id, [])

                        # Tạo object UserTask (chưa save vào DB ngay)
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

                # 3. Lưu toàn bộ UserTask của tất cả Trainee cùng lúc (Chỉ 1 câu query INSERT)
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
    """
    ViewSet này quản lý mọi thứ về Course:
    - CRUD cơ bản (GET, POST, PUT, PATCH, DELETE course)
    - Các action mở rộng: manage supervisors, trainees, subjects
    """

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSupervisor]

    # =================================================
    # 1. QUẢN LÝ SUPERVISORS
    # =================================================

    @action(detail=True, methods=["post"], url_path="add-supervisors")
    def add_supervisors(self, request, pk=None):
        course = self.get_object()
        serializer = AddSupervisorSerializer(data=request.data)
        if serializer.is_valid():
            supervisor_ids = serializer.validated_data["supervisor_ids"]

            # Lọc những người chưa có trong khóa học để tránh lỗi duplicate
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

    # =================================================
    # 2. QUẢN LÝ TRAINEES
    # =================================================

    @action(detail=True, methods=["post"], url_path="add-trainees")
    def add_trainees(self, request, course_id=None):
        course = get_object_or_404(Course, pk=course_id)

        # 2. Validate Input qua Serializer
        serializer = AddTraineeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Lấy danh sách User object từ serializer (nhờ PrimaryKeyRelatedField)
        trainees = serializer.validated_data["trainee_ids"]

        # ==================================================
        # BƯỚC CHUẨN BỊ DỮ LIỆU (TỐI ƯU PERFORMANCE)
        # ==================================================

        # Lấy tất cả CourseSubject của khóa học này 1 lần duy nhất
        course_subjects = list(CourseSubject.objects.filter(course=course))

        # Lấy tất cả Task của các CourseSubject đó 1 lần duy nhất
        # Map: { course_subject_id: [list_of_tasks] }
        tasks_map = {}

        # Lấy tất cả task có type là COURSE_SUBJECT và ID nằm trong list course_subjects
        cs_ids = [cs.id for cs in course_subjects]
        relevant_tasks = Task.objects.filter(
            taskable_type=Task.TaskType.COURSE_SUBJECT, taskable_id__in=cs_ids
        )

        # Gom nhóm task theo course_subject_id để dễ truy xuất
        for task in relevant_tasks:
            if task.taskable_id not in tasks_map:
                tasks_map[task.taskable_id] = []
            tasks_map[task.taskable_id].append(task)

        # ==================================================
        # BƯỚC XỬ LÝ GHI DỮ LIỆU (TRANSACTION)
        # ==================================================

        added_count = 0
        skipped_count = 0
        all_user_tasks_to_create = (
            []
        )  # List chứa tất cả UserTask để bulk_create cuối cùng

        try:
            with transaction.atomic():
                for trainee in trainees:
                    # Kiểm tra nếu trainee đã trong khóa học rồi thì bỏ qua
                    if UserCourse.objects.filter(user=trainee, course=course).exists():
                        skipped_count += 1
                        continue

                    # 1. Tạo UserCourse
                    user_course = UserCourse.objects.create(
                        user=trainee,
                        course=course,
                        status=UserCourse.Status.NOT_STARTED,
                    )

                    # 2. Tạo UserSubject & UserTask cho từng môn
                    for cs in course_subjects:
                        # Tạo UserSubject
                        user_subject = UserSubject.objects.create(
                            user=trainee,
                            user_course=user_course,
                            course_subject=cs,
                            status=UserSubject.Status.NOT_STARTED,
                        )

                        # Lấy các task thuộc môn học này từ Map đã chuẩn bị
                        tasks_of_cs = tasks_map.get(cs.id, [])

                        # Tạo object UserTask (chưa save vào DB ngay)
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

                # 3. Lưu toàn bộ UserTask của tất cả Trainee cùng lúc (Chỉ 1 câu query INSERT)
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

            # Xóa UserCourse -> Django CASCADE sẽ tự xóa UserSubject và UserTask
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

    # =================================================
    # 3. QUẢN LÝ SUBJECTS (MÔN HỌC)
    # =================================================

    @action(detail=True, methods=["post"], url_path="add-subject")
    def add_subject(self, request, pk=None):
        # 1. Lấy Course chuẩn theo ViewSet
        course = self.get_object()

        # 2. Validate dữ liệu
        serializer = AddSubjectTaskSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        subject_id = data.get("subject_id")
        task_names = data.get("tasks", [])

        try:
            with transaction.atomic():
                # --- BIẾN ĐỂ LƯU LIST TASK DÙNG ĐỂ GÁN CHO USER ---
                final_tasks_for_user = []

                # =================================================
                # TRƯỜNG HỢP A: SUBJECT CÓ SẴN
                # =================================================
                if subject_id:
                    subject = Subject.objects.get(pk=subject_id)

                    # Tạo liên kết
                    course_subject = CourseSubject.objects.create(
                        course=course,
                        subject=subject,
                    )

                    # Clone Tasks từ Subject -> CourseSubject
                    template_tasks = Task.objects.filter(
                        taskable_type=Task.TaskType.SUBJECT, taskable_id=subject.id
                    )

                    new_tasks = []
                    # Clone task cũ
                    for template in template_tasks:
                        new_tasks.append(
                            Task(
                                name=template.name,
                                taskable_type=Task.TaskType.COURSE_SUBJECT,  # Gán vào CS
                                taskable_id=course_subject.id,
                            )
                        )

                    # Tạo task mới từ request
                    for name in task_names:
                        new_tasks.append(
                            Task(
                                name=name,
                                taskable_type=Task.TaskType.COURSE_SUBJECT,  # Gán vào CS
                                taskable_id=course_subject.id,
                            )
                        )

                    # Lưu vào DB
                    created_tasks = Task.objects.bulk_create(new_tasks)

                    # Update list task để tí nữa gán cho user
                    final_tasks_for_user = created_tasks
                    message = "Added existing subject and cloned tasks successfully."

                # =================================================
                # TRƯỜNG HỢP B: SUBJECT MỚI
                # =================================================
                else:
                    # Tạo Subject
                    subject = Subject.objects.create(
                        name=data["name"],
                        max_score=data["max_score"],
                        estimated_time_days=data["estimated_time_days"],
                        image=data.get("image"),
                    )

                    # Tạo Tasks gắn vào Subject
                    new_tasks = []
                    for name in task_names:
                        new_tasks.append(
                            Task(
                                name=name,
                                taskable_type=Task.TaskType.SUBJECT,  # Gán vào Subject gốc
                                taskable_id=subject.id,
                            )
                        )

                    created_tasks = Task.objects.bulk_create(new_tasks)

                    # Tạo liên kết
                    course_subject = CourseSubject.objects.create(
                        course=course, subject=subject
                    )

                    # Update list task để tí nữa gán cho user
                    final_tasks_for_user = created_tasks
                    message = "Created new subject and template tasks successfully."

                # =================================================
                # QUAN TRỌNG: ĐỒNG BỘ CHO TRAINEE ĐANG CÓ TRONG KHÓA
                # =================================================

                # Lấy tất cả UserCourse của khóa học này
                existing_user_courses = UserCourse.objects.filter(course=course)

                if existing_user_courses.exists():
                    new_user_subjects = []
                    new_user_tasks = []

                    for uc in existing_user_courses:
                        # 1. Tạo UserSubject cho môn mới này
                        # Lưu ý: Cần create luôn để lấy ID gán cho UserTask bên dưới
                        # (Không bulk_create UserSubject được vì cần ID ngay)
                        user_subject = UserSubject.objects.create(
                            user=uc.user,
                            user_course=uc,
                            course_subject=course_subject,
                            status=UserSubject.Status.NOT_STARTED,
                        )

                        # 2. Tạo UserTask dựa trên list task vừa tạo ở trên
                        for task in final_tasks_for_user:
                            new_user_tasks.append(
                                UserTask(
                                    user=uc.user,
                                    task=task,
                                    user_subject=user_subject,
                                    status=UserTask.Status.NOT_DONE,
                                )
                            )

                    # Bulk create UserTask (số lượng lớn)
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
        # Nhận vào ID của CourseSubject (không phải ID của Subject gốc)
        serializer = DeleteIDSerializer(data=request.data)

        if serializer.is_valid():
            cs_id = serializer.validated_data["id"]

            # Xóa CourseSubject -> Django CASCADE sẽ xóa UserSubject liên quan
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
