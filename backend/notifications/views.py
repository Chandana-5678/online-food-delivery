from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer
class NotificationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    serializer_class = NotificationSerializer; filterset_fields = ("is_read", "notification_type")
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Notification.objects.none()
        return Notification.objects.filter(user=self.request.user)
    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        obj = self.get_object(); obj.is_read = True; obj.save(); return Response(self.get_serializer(obj).data)
    @action(detail=False, methods=["post"])
    def mark_all_read(self, request):
        self.get_queryset().update(is_read=True); return Response({"detail": "All notifications marked read."})
