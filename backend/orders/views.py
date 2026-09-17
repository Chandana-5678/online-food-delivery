from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import Order
from .serializers import OrderCreateSerializer, OrderSerializer
from .services import create_order


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    filterset_fields = ("status", "payment_status", "restaurant"); search_fields = ("order_number",); ordering_fields = ("created_at", "grand_total")
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Order.objects.none()
        user = self.request.user; qs = Order.objects.select_related("restaurant", "customer", "delivery_address", "delivery_partner__user").prefetch_related("items", "status_events")
        if user.is_staff or user.role == "admin": return qs
        if user.role == "customer": return qs.filter(customer=user)
        if user.role == "restaurant_owner": return qs.filter(restaurant__owner=user)
        if user.role == "delivery_partner": return qs.filter(delivery_partner__user=user)
        return qs.none()
    def get_serializer_class(self): return OrderCreateSerializer if self.action == "create" else OrderSerializer
    def create(self, request, *args, **kwargs):
        if request.user.role != "customer": raise PermissionDenied("Customer role required.")
        serializer = self.get_serializer(data=request.data); serializer.is_valid(raise_exception=True)
        order = create_order(request.user, serializer.validated_data["delivery_address"], serializer.validated_data["payment_method"], serializer.validated_data.get("customer_notes", ""))
        return Response(OrderSerializer(order, context={"request": request}).data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=["post"])
    def transition(self, request, pk=None):
        order = self.get_object(); order.transition(request.data.get("status"), request.user); return Response(OrderSerializer(order).data)
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object(); order.transition(Order.Status.CANCELLED, request.user); return Response(OrderSerializer(order).data)
