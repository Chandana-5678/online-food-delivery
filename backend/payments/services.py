from uuid import uuid4
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from notifications.services import notify
from .models import Payment
@transaction.atomic
def process_mock_payment(payment, succeed):
    if payment.payment_method != Payment.Method.ONLINE: raise ValidationError("This order is not an online payment.")
    if payment.status == Payment.Status.SUCCESSFUL: raise ValidationError("Payment is already complete.")
    payment.transaction_id = f"MOCK-{uuid4().hex.upper()}"; payment.status = Payment.Status.SUCCESSFUL if succeed else Payment.Status.FAILED; payment.payment_date = timezone.now(); payment.save()
    payment.order.payment_status = payment.status; payment.order.save(update_fields=["payment_status"])
    notify(payment.customer, f"Payment {payment.get_status_display()}", f"Payment for {payment.order.order_number} is {payment.get_status_display().lower()}.", "payment")
    return payment
