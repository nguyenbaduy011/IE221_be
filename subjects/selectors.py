from django.db.models import Q
from subjects.models.subject import Subject
from subjects.models.category import Category

def get_all_subjects():
    return Subject.objects.all().order_by('name')

def get_subject_by_id(subject_id):
    try:
        return Subject.objects.get(id=subject_id)
    except Subject.DoesNotExist:
        return None

def search_subjects(query=None, exclude_ids=None):
    """
    Logic search tương tự file Ruby: search_subjects và excluded_subject_ids
    """
    subjects = Subject.objects.all()

    if exclude_ids:
        subjects = subjects.exclude(id__in=exclude_ids)

    if query:
        subjects = subjects.filter(name__icontains=query)
    
    return subjects.order_by('name')


def search_categories(query=None):
    """
    Logic tương tự scope :recent và :search_by_name trong Rails
    """
    categories = Category.objects.all()

    if query:
        categories = categories.filter(name__icontains=query)
    
    return categories.order_by('-created_at')

def get_category_by_id(category_id):
    try:
        return Category.objects.prefetch_related('subjectcategory_set__subject').get(id=category_id)
    except Category.DoesNotExist:
        return None