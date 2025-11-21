from rest_framework import serializers
from django.db import transaction
from subjects.models.category import Category
from subjects.models.subject_category import SubjectCategory
from subjects.serializers.subject_serializers import SubjectSerializer
from subjects.models.subject import Subject

class SubjectCategorySerializer(serializers.ModelSerializer):
    """
    Dùng để hiển thị thông tin Subject lồng trong Category
    """
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='subject', write_only=True
    )

    class Meta:
        model = SubjectCategory
        fields = ['id', 'subject', 'subject_id', 'position']


class CategorySerializer(serializers.ModelSerializer):
    # Dùng serializer lồng nhau để vừa đọc vừa ghi được
    subject_categories = SubjectCategorySerializer(source='subjectcategory_set', many=True, read_only=False)

    class Meta:
        model = Category
        fields = ['id', 'name', 'subject_categories', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        # Tách dữ liệu subject_categories ra khỏi data của Category
        subject_categories_data = validated_data.pop('subjectcategory_set', [])
        
        # 1. Tạo Category
        category = Category.objects.create(**validated_data)

        # 2. Tạo các record trong bảng trung gian
        for index, item in enumerate(subject_categories_data):
            SubjectCategory.objects.create(
                category=category,
                subject=item['subject'],
                position=index + 1 # Tự động đánh số thứ tự dựa trên list gửi lên
            )
        
        return category

    @transaction.atomic
    def update(self, instance, validated_data):
        subject_categories_data = validated_data.pop('subjectcategory_set', [])

        # 1. Update thông tin cơ bản
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        # 2. Xử lý danh sách môn học (Chiến lược: Xóa hết cũ -> Tạo mới để đảm bảo thứ tự chính xác)
        # Lưu ý: Nếu cần giữ lại ID của bảng trung gian thì logic sẽ phức tạp hơn, 
        # nhưng với yêu cầu hiện tại thì cách xóa đi tạo lại là an toàn nhất cho thứ tự.
        if subject_categories_data is not None:
            instance.subjectcategory_set.all().delete()
            
            for index, item in enumerate(subject_categories_data):
                SubjectCategory.objects.create(
                    category=instance,
                    subject=item['subject'],
                    position=index + 1
                )

        return instance