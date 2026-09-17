from django.utils import timezone
from rest_framework import permissions, viewsets
from .models import Coupon
from .serializers import CouponSerializer
class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = CouponSerializer; search_fields = ("code", "description"); ordering_fields = ("expiry_date", "minimum_order_amount")
    def get_queryset(self):
        qs = Coupon.objects.all()
        return qs if self.request.user.is_staff else qs.filter(is_active=True, start_date__lte=timezone.now(), expiry_date__gte=timezone.now())
    def get_permissions(self): return [permissions.IsAdminUser()] if self.action not in ("list", "retrieve") else [permissions.IsAuthenticated()]
