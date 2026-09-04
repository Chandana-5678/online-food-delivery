from django.db.models import Sum
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from orders.models import Order
from orders.serializers import OrderSerializer
from .models import DeliveryPartner
from .serializers import DeliveryPartnerSerializer, EarningsSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = DeliveryPartnerSerializer
    def get_object(self):
        if self.request.user.role != "delivery_partner": raise PermissionDenied("Delivery partner role required.")
        return DeliveryPartner.objects.get(user=self.request.user)


class AvailableDeliveriesView(generics.ListAPIView):
    serializer_class = OrderSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Order.objects.none()
        if self.request.user.role != "delivery_partner": raise PermissionDenied("Delivery partner role required.")
        return Order.objects.filter(status=Order.Status.READY, delivery_partner__isnull=True).select_related("restaurant", "delivery_address")


class AssignedDeliveriesView(generics.ListAPIView):
    serializer_class = OrderSerializer
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Order.objects.none()
        return Order.objects.filter(delivery_partner__user=self.request.user).select_related("restaurant", "delivery_address")


class AcceptDeliveryView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    def post(self, request, pk):
        partner = DeliveryPartner.objects.get(user=request.user); order = generics.get_object_or_404(Order, pk=pk, status=Order.Status.READY, delivery_partner__isnull=True)
        order.transition(Order.Status.ASSIGNED, request.user, delivery_partner=partner); return Response(OrderSerializer(order).data)


class EarningsView(generics.GenericAPIView):
    serializer_class = EarningsSerializer
    def get(self, request):
        qs = Order.objects.filter(delivery_partner__user=request.user, status=Order.Status.DELIVERED)
        earnings = qs.aggregate(total=Sum("delivery_fee"))["total"] or 0
        return Response({"completed_deliveries": qs.count(), "total_earnings": earnings})
