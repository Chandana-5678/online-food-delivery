from django.conf import settings
from django.db import models
class Payment(models.Model):
    class Method(models.TextChoices): COD = "cod", "Cash on Delivery"; ONLINE = "online", "Mock Online Payment"
    class Status(models.TextChoices): PENDING = "pending", "Pending"; SUCCESSFUL = "successful", "Successful"; FAILED = "failed", "Failed"; REFUNDED = "refunded", "Refunded"
    order = models.OneToOneField("orders.Order", on_delete=models.CASCADE, related_name="payment")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2); payment_method = models.CharField(max_length=10, choices=Method.choices)
    transaction_id = models.CharField(max_length=80, blank=True, unique=True, null=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING); payment_date = models.DateTimeField(null=True, blank=True)
