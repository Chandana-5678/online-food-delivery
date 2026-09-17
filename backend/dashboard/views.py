from django.db.models import Count, DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework import generics, serializers, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from accounts.models import User
from accounts.serializers import UserSerializer
from delivery.models import DeliveryPartner
from notifications.models import Notification
from orders.models import Order, OrderItem
from restaurants.models import Restaurant

ZERO = Value(0, output_field=DecimalField())


class DashboardSerializer(serializers.Serializer):
    data = serializers.JSONField(read_only=True)


class DashboardView(generics.GenericAPIView):
    serializer_class = DashboardSerializer
    def get(self, request):
        user = request.user; today = timezone.localdate()
        if user.is_staff or user.role == "admin": return Response(self.admin_data(today))
        if user.role == "restaurant_owner": return Response(self.restaurant_data(user, today))
        if user.role == "delivery_partner": return Response(self.delivery_data(user, today))
        return Response(self.customer_data(user))
    def admin_data(self, today):
        orders = Order.objects.all()
        return {"total_users": User.objects.count(), "total_customers": User.objects.filter(role="customer").count(),
            "total_restaurants": Restaurant.objects.count(), "total_delivery_partners": DeliveryPartner.objects.count(),
            "total_orders": orders.count(), "today_orders": orders.filter(created_at__date=today).count(),
            "pending_orders": orders.filter(status__in=("pending", "confirmed")).count(), "completed_orders": orders.filter(status="delivered").count(),
            "cancelled_orders": orders.filter(status__in=("cancelled", "rejected")).count(),
            "total_revenue": orders.filter(status="delivered").aggregate(v=Coalesce(Sum("grand_total"), ZERO))["v"],
            "today_revenue": orders.filter(status="delivered", delivered_at__date=today).aggregate(v=Coalesce(Sum("grand_total"), ZERO))["v"],
            "top_restaurants": list(Restaurant.objects.annotate(order_count=Count("orders")).order_by("-order_count").values("id", "name", "order_count")[:5]),
            "top_selling_foods": list(OrderItem.objects.values("food_name").annotate(quantity=Sum("quantity")).order_by("-quantity")[:5])}
    def restaurant_data(self, user, today):
        orders = Order.objects.filter(restaurant__owner=user)
        return {"total_orders": orders.count(), "today_orders": orders.filter(created_at__date=today).count(), "pending_orders": orders.filter(status__in=("pending", "confirmed", "accepted")).count(),
            "preparing_orders": orders.filter(status="preparing").count(), "completed_orders": orders.filter(status="delivered").count(),
            "revenue": orders.filter(status="delivered").aggregate(v=Coalesce(Sum("grand_total"), ZERO))["v"],
            "today_revenue": orders.filter(status="delivered", delivered_at__date=today).aggregate(v=Coalesce(Sum("grand_total"), ZERO))["v"],
            "top_selling_items": list(OrderItem.objects.filter(order__restaurant__owner=user).values("food_name").annotate(quantity=Sum("quantity")).order_by("-quantity")[:5]),
            "average_rating": Restaurant.objects.filter(owner=user).aggregate(v=Coalesce(Sum("average_rating"), ZERO))["v"]}
    def delivery_data(self, user, today):
        orders = Order.objects.filter(delivery_partner__user=user); delivered = orders.filter(status="delivered")
        return {"available_deliveries": Order.objects.filter(status="ready", delivery_partner__isnull=True).count(),
            "active_delivery": orders.exclude(status="delivered").values("id", "order_number", "status").first(),
            "today_deliveries": delivered.filter(delivered_at__date=today).count(), "completed_deliveries": delivered.count(),
            "today_earnings": delivered.filter(delivered_at__date=today).aggregate(v=Coalesce(Sum("delivery_fee"), ZERO))["v"],
            "total_earnings": delivered.aggregate(v=Coalesce(Sum("delivery_fee"), ZERO))["v"]}
    def customer_data(self, user):
        orders = Order.objects.filter(customer=user)
        return {"recent_orders": list(orders.values("id", "order_number", "status", "grand_total", "created_at")[:5]),
            "current_order": orders.exclude(status__in=("delivered", "cancelled", "rejected")).values("id", "order_number", "status").first(),
            "favorite_restaurants": user.favorites.count(), "saved_addresses": user.addresses.count(), "unread_notifications": Notification.objects.filter(user=user, is_read=False).count()}


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "role", "is_active", "date_joined", "password")
        read_only_fields = ("id", "date_joined")
    def create(self, validated_data):
        password = validated_data.pop("password", None)
        return User.objects.create_user(password=password, **validated_data)
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        instance = super().update(instance, validated_data)
        if password: instance.set_password(password); instance.save(update_fields=["password"])
        return instance


class UserAdminViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by("-date_joined"); serializer_class = AdminUserSerializer; search_fields = ("email", "first_name", "last_name"); filterset_fields = ("role", "is_active")
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if not request.user.is_staff: raise PermissionDenied("Administrator access required.")
