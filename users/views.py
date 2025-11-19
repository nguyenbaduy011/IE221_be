from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q 
from authen.models import CustomUser
from authen.permissions import IsAdminRole
from .serializers import (
    AdminUserListSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
    AdminUserBulkCreateSerializer
)

class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminRole]
    serializer_class = AdminUserListSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        return AdminUserListSerializer

    def get_queryset(self):
        # Sắp xếp theo ngày tham gia mới nhất
        queryset = CustomUser.objects.all().order_by('-date_joined')
        
        # 1. Xử lý Search
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(email__icontains=search) | 
                Q(full_name__icontains=search)
            )

        # 2. Xử lý Role (Frontend gửi chuỗi rỗng nếu là ALL, hoặc backend tự check)
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

    # --- Override để bọc Response theo chuẩn ApiResponse { status, message, data } ---

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Lấy danh sách thành công",
            "data": response.data
        })

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Tạo user thành công",
            "data": response.data
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Cập nhật thành công",
            "data": response.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response({
            "status": "success",
            "message": "Xóa thành công",
            "data": None
        }, status=status.HTTP_200_OK)

    # --- Actions ---

    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user.id == request.user.id:
            return Response({"status": "error", "message": "Không thể tự khóa chính mình"}, status=400)
        user.is_active = False
        user.save()
        return Response({"status": "success", "message": "Đã khóa tài khoản", "data": None}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "success", "message": "Đã mở khóa tài khoản", "data": None}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_add(self, request):
        serializer = AdminUserBulkCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        users = serializer.save()
        return Response({
            "status": "success",
            "message": f"{len(users)} users created successfully",
            "data": [{"id": u.id, "email": u.email, "full_name": u.full_name} for u in users]
        }, status=201)

    @action(detail=False, methods=['post'])
    def bulk_delete(self, request):
        ids = request.data.get("ids", [])
        if not ids:
            return Response({"status": "error", "message": "No user IDs provided"}, status=400)
        
        users = CustomUser.objects.filter(id__in=ids)
        count = users.count()
        users.delete()
        return Response({"status": "success", "message": f"{count} users deleted", "data": None})
