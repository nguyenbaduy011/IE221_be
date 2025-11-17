from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from authen.models import CustomUser

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    commentable = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"Comment by {self.user.email} on {self.content_type} {self.object_id}"

    def clean(self):
        if not self.content.strip():
            raise ValidationError("Comment content cannot be empty.")
        
        if len(self.content) < 5:
            raise ValidationError("Comment content must be at least 5 characters long.")

        if len(self.content) > 500:
            raise ValidationError("Comment content cannot exceed 500 characters.")
