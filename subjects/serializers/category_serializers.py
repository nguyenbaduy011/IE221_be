from rest_framework import serializers
from subjects.models.category import Category
from subjects.models.subject_category import SubjectCategory
from subjects.serializers.subject_serializers import SubjectSerializer

class SubjectCategorySerializer(serializers.ModelSerializer):
    """
    Serializer cho bảng trung gian để lấy thông tin Subject kèm Position
    """
    subject = SubjectSerializer(read_only=True)

    class Meta:
        model = SubjectCategory
        fields = ['id', 'subject', 'position']


class CategorySerializer(serializers.ModelSerializer):
    subject_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'subject_categories', 'created_at', 'updated_at']

    def get_subject_categories(self, obj):
        # Lấy các record bảng trung gian, sắp xếp theo position
        qs = obj.subjectcategory_set.select_related('subject').order_by('position')
        return SubjectCategorySerializer(qs, many=True).data