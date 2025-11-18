from django.db.models import Q
from subjects.models import Subject

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