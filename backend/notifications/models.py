from django.conf import settings
from django.db import models
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=140); message = models.TextField(); notification_type = models.CharField(max_length=40, default="general")
    is_read = models.BooleanField(default=False); created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta: ordering = ("-created_at",)
