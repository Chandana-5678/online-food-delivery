from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from .services import process_mock_payment
class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PaymentSerializer; filterset_fields = ("status", "payment_method")
    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False): return Payment.objects.none()
        qs = Payment.objects.select_related("order", "customer")
        return qs if self.request.user.is_staff else qs.filter(customer=self.request.user)
class MockCheckoutView(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    def post(self, request, pk):
        payment = generics.get_object_or_404(Payment, pk=pk, customer=request.user)
        return Response(PaymentSerializer(process_mock_payment(payment, bool(request.data.get("success", True)))).data)
