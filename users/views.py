from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q 
from authen.models import CustomUser
from authen.permissions import IsAdminRole, IsAdminOrSupervisor # Import thêm IsAdminOrSupervisor
from .serializers import (
    AdminUserListSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    AdminUserBulkCreateSerializer
)

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