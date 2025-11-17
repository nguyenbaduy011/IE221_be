from rest_framework import viewsets, status
from rest_framework.decorators import action # <--- Import cái này
from rest_framework.response import Response
from authen.models import CustomUser
from authen.permissions import IsAdminRole # Import permission (hoặc move file này sang users luôn)
from .serializers import (
    AdminUserListSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer
)

class AdminUserViewSet(viewsets.ModelViewSet):
    """
    API Quản lý User (Chỉ Admin)
    Endpoint: /api/users/
    """
    permission_classes = [IsAdminRole]
    queryset = CustomUser.objects.all().order_by('-date_joined')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return AdminUserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AdminUserUpdateSerializer
        return AdminUserListSerializer

    @action(detail=True, methods=['post'], url_path='deactivate')
    def deactivate_user(self, request, pk=None):
        user = self.get_object()
        
        if user == request.user:
            return Response({
                "status": "error",
                "message": "Bạn không thể tự khóa tài khoản của chính mình.",
                "data": None
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = False
        user.save()
        
        return Response({
            "status": "success",
            "message": f"Đã vô hiệu hóa user {user.email}.",
            "data": None
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='activate')
    def activate_user(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        
        return Response({
            "status": "success",
            "message": f"Đã kích hoạt lại user {user.email}.",
            "data": None
        }, status=status.HTTP_200_OK)