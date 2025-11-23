from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from users.models.user_subject import UserSubject
from authen import permissions
from users.models.comment import Comment
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q 
from authen.models import CustomUser
from authen.permissions import IsAdminRole, IsAdminOrSupervisor, IsCommentOwnerOrAdmin, IsOwner, IsTraineeRole # Import thêm IsAdminOrSupervisor
from users.serializers import (
    AdminUserListSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    AdminUserBulkCreateSerializer,
    CommentSerializer,
    TraineeEnrolledSubjectSerializer,
    TraineeTaskUpdateSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from rest_framework.parsers import MultiPartParser, FormParser

from users.models.user_task import UserTask




class UserViewSet(viewsets.ModelViewSet):
    # Cho phép cả Admin và Supervisor truy cập
    permission_classes = [IsAdminOrSupervisor]
    serializer_class = AdminUserListSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        return AdminUserListSerializer

    def get_queryset(self):
        user = self.request.user
        
        # Sắp xếp theo ngày tham gia mới nhất
        queryset = CustomUser.objects.all().order_by('-date_joined')

        # --- LOGIC 1: PHÂN QUYỀN DỮ LIỆU ---
        # Nếu là Supervisor: KHÔNG ĐƯỢC xem Admin, chỉ xem Trainee và Supervisor khác
        if user.role == 'SUPERVISOR':
            queryset = queryset.exclude(role='ADMIN')
        
        # 1. Xử lý Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | 
                Q(full_name__icontains=search)
            )

        # 2. Xử lý Role
        role = self.request.query_params.get('role')
        if role and role != 'ALL':
            queryset = queryset.filter(role=role)

        # 3. Xử lý Status
        status_param = self.request.query_params.get('status')
        if status_param == 'ACTIVE':
            queryset = queryset.filter(is_active=True)
        elif status_param == 'INACTIVE':
            queryset = queryset.filter(is_active=False)
            
        return queryset

    # --- XÓA DELETE VÀ BULK DELETE ---
    # Override destroy để chặn xóa user (trả về 405 Method Not Allowed)
    def destroy(self, request, *args, **kwargs):
        return Response(
            {"status": "error", "message": "Hệ thống không cho phép xóa User. Vui lòng Deactivate."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    # --- Actions ---

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user.id == request.user.id:
            return Response({"status": "error", "message": "Không thể tự khóa chính mình"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Supervisor không được khóa Admin (dù queryset đã lọc, nhưng check thêm cho chắc)
        if request.user.role == 'SUPERVISOR' and user.role == 'ADMIN':
             return Response({"status": "error", "message": "Không có quyền khóa Admin"}, status=status.HTTP_403_FORBIDDEN)

        user.is_active = False
        user.save()
        return Response({"status": "success", "message": "Đã khóa tài khoản", "data": None}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        
        if request.user.role == 'SUPERVISOR' and user.role == 'ADMIN':
             return Response({"status": "error", "message": "Không có quyền mở khóa Admin"}, status=status.HTTP_403_FORBIDDEN)

        user.is_active = True
        user.save()
        return Response({"status": "success", "message": "Đã mở khóa tài khoản", "data": None}, status=status.HTTP_200_OK)

    # --- BULK ACTIONS MỚI ---

    @action(detail=False, methods=['post'])
    def bulk_deactivate(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"status": "error", "message": "No user IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Lọc user hợp lệ để deactivate
        users = CustomUser.objects.filter(id__in=ids)
        
        # Logic bảo vệ: Bỏ qua chính mình và Admin (nếu người gọi là Supervisor)
        if request.user.role == 'SUPERVISOR':
            users = users.exclude(role='ADMIN')
        users = users.exclude(id=request.user.id)

        count = users.count()
        users.update(is_active=False)
        
        return Response({
            "status": "success", 
            "message": f"Đã khóa {count} users thành công", 
            "data": None
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_activate(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"status": "error", "message": "No user IDs provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        users = CustomUser.objects.filter(id__in=ids)
        
        if request.user.role == 'SUPERVISOR':
            users = users.exclude(role='ADMIN')
            
        count = users.count()
        users.update(is_active=True)
        
        return Response({
            "status": "success", 
            "message": f"Đã kích hoạt {count} users thành công", 
            "data": None
        }, status=status.HTTP_200_OK)

    # Giữ nguyên logic create, bulk_add, list, update như cũ...
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "status": "success", "message": "Lấy danh sách thành công", "data": response.data
        }, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # Supervisor không được tạo user (nếu muốn chặt chẽ hơn)
        if request.user.role == 'SUPERVISOR':
             return Response({"status": "error", "message": "Supervisor không có quyền tạo User"}, status=status.HTTP_403_FORBIDDEN)

        response = super().create(request, *args, **kwargs)
        return Response({
            "status": "success", "message": "Tạo user thành công", "data": response.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
         # Supervisor không được sửa thông tin user
        if request.user.role == 'SUPERVISOR':
             return Response({"status": "error", "message": "Supervisor không có quyền sửa User"}, status=status.HTTP_403_FORBIDDEN)
             
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": "success", "message": "Cập nhật thành công", "data": response.data
        }, status=status.HTTP_200_OK)
        
    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        if request.user.role == 'SUPERVISOR':
             return Response({"status": "error", "message": "Supervisor không có quyền Bulk Add"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AdminUserBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = serializer.save()
        return Response({
            "status": "success",
            "message": f"{len(users)} users created successfully",
            "data": [{"id": u.id, "email": u.email, "full_name": u.full_name} for u in users]
        }, status=status.HTTP_201_CREATED)
    
class CommentViewSet(viewsets.ModelViewSet):
    """
    API cho Comment.
    Hỗ trợ lọc: /api/resources/comments/?model_name=task&object_id=1
    """
    serializer_class = CommentSerializer
    permission_classes = [IsCommentOwnerOrAdmin]
    queryset = Comment.objects.all().order_by('created_at')

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Lấy tham số từ URL
        model_name = self.request.query_params.get('model_name')
        object_id = self.request.query_params.get('object_id')

        if model_name and object_id:
            try:
                ct = ContentType.objects.get(model=model_name.lower())
                queryset = queryset.filter(content_type=ct, object_id=object_id)
            except ContentType.DoesNotExist:
                return queryset.none()
        
        return queryset

class UserTaskViewSet(mixins.RetrieveModelMixin, 
                      mixins.UpdateModelMixin, 
                      viewsets.GenericViewSet):
    """
    API cho Trainee tương tác với Task của mình:
    - PATCH /api/user-tasks/{id}/: Update status, spent_time, upload file
    """
    serializer_class = TraineeTaskUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwner]
    parser_classes = (MultiPartParser, FormParser) # Quan trọng để upload file

    def get_queryset(self):
        # Chỉ lấy các task thuộc về user đang đăng nhập
        return UserTask.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        # Support cả PUT và PATCH
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Logic: Nếu checkbox checked -> Status = DONE, unchecked -> NOT_DONE
        # Frontend gửi lên: status=1 (Done) hoặc status=0 (Not Done)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Cập nhật task thành công",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class TraineeMySubjectsView(APIView):
    """
    API lấy danh sách các môn học CỦA TÔI (My Subjects)
    kèm theo điểm số [b]/[c]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        # Query lấy tất cả UserSubject của user hiện tại
        # Sử dụng select_related để tối ưu truy vấn (tránh N+1 query)
        # Đi từ UserSubject -> CourseSubject -> Subject
        my_subjects = UserSubject.objects.filter(user=user).select_related(
            'course_subject', 
            'course_subject__subject'
        ).order_by('-created_at')

        serializer = TraineeEnrolledSubjectSerializer(my_subjects, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
class TraineeSubjectActionViewSet(viewsets.ModelViewSet):
    """
    ViewSet xử lý các hành động của Trainee với Subject
    """
    serializer_class = TraineeEnrolledSubjectSerializer
    permission_classes = [IsTraineeRole] 

    def get_queryset(self):
        return UserSubject.objects.filter(user=self.request.user)

    # API cập nhật ngày thực tế (Actual Start/End)
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Chỉ cho phép update ngày bắt đầu/kết thúc thực tế
        # Frontend gửi lên: { "actual_start_day": "2023-11-20", "actual_end_day": ... }
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            "message": "Cập nhật thời gian thực tế thành công",
            "data": serializer.data
        })

    # API Xử lý nút "Hoàn thành" (Dùng cho cả nút Inprogress và Finish)
    @action(detail=True, methods=['post'])
    def finish_subject(self, request, pk=None):
        user_subject = self.get_object()

        with transaction.atomic():
            # 1. Update trạng thái tất cả các Task con thành DONEvvv
            user_tasks = user_subject.user_tasks.all()
            user_tasks.update(status=UserTask.Status.DONE)

            # 2. Update trạng thái Môn học
            # Logic: Kiểm tra xem nộp đúng hạn hay trễ hạn
            now = timezone.now()
            deadline = user_subject.course_subject.finish_date
            
            # Mặc định chuyển thành 'Finish' (Logic chi tiết Status tùy bạn: EARLY, ON_TIME, OVERDUE...)
            # Dựa trên file user_subject.py của bạn:
            if deadline and now.date() <= deadline:
                new_status = UserSubject.Status.FINISHED_ON_TIME
            elif deadline and now.date() > deadline:
                new_status = UserSubject.Status.FINISED_BUT_OVERDUE
            else:
                new_status = UserSubject.Status.FINISHED_ON_TIME # Fallback

            user_subject.status = new_status
            
            # Cập nhật ngày kết thúc thực tế nếu chưa có
            if not user_subject.completed_at:
                user_subject.completed_at = now
            
            user_subject.save()

        # Trả về data mới nhất để Frontend update UI
        serializer = self.get_serializer(user_subject)
        return Response({
            "message": "Đã hoàn thành môn học và tất cả nhiệm vụ.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    
