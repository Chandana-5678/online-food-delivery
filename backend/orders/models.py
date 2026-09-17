from django.conf import settings
from django.db import models, transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from accounts.models import Address
from coupons.models import Coupon
from menu.models import FoodItem
from restaurants.models import Restaurant


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"; CONFIRMED = "confirmed", "Confirmed"; ACCEPTED = "accepted", "Accepted"
        PREPARING = "preparing", "Preparing"; READY = "ready", "Ready for Pickup"; ASSIGNED = "assigned", "Assigned to Delivery Partner"
        PICKED_UP = "picked_up", "Picked Up"; ON_THE_WAY = "on_the_way", "On the Way"; DELIVERED = "delivered", "Delivered"
        CANCELLED = "cancelled", "Cancelled"; REJECTED = "rejected", "Rejected"
    TRANSITIONS = {Status.PENDING: {Status.CONFIRMED, Status.ACCEPTED, Status.CANCELLED, Status.REJECTED},
        Status.CONFIRMED: {Status.ACCEPTED, Status.CANCELLED, Status.REJECTED}, Status.ACCEPTED: {Status.PREPARING, Status.CANCELLED},
        Status.PREPARING: {Status.READY}, Status.READY: {Status.ASSIGNED}, Status.ASSIGNED: {Status.PICKED_UP},
        Status.PICKED_UP: {Status.ON_THE_WAY}, Status.ON_THE_WAY: {Status.DELIVERED}}
    order_number = models.CharField(max_length=32, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")
    restaurant = models.ForeignKey(Restaurant, on_delete=models.PROTECT, related_name="orders")
    delivery_partner = models.ForeignKey("delivery.DeliveryPartner", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    delivery_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, related_name="orders")
    delivery_address_snapshot = models.JSONField(default=dict)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2); tax = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=12, decimal_places=2); discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2); coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=(("cod", "Cash on Delivery"), ("online", "Mock Online Payment")))
    payment_status = models.CharField(max_length=12, default="pending")
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING, db_index=True)
    customer_notes = models.TextField(blank=True); created_at = models.DateTimeField(auto_now_add=True, db_index=True); updated_at = models.DateTimeField(auto_now=True)
    accepted_at = models.DateTimeField(null=True, blank=True); prepared_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True); delivered_at = models.DateTimeField(null=True, blank=True); cancelled_at = models.DateTimeField(null=True, blank=True)
    class Meta: ordering = ("-created_at",); indexes = [models.Index(fields=("restaurant", "status")), models.Index(fields=("customer", "created_at"))]
    @transaction.atomic
    def transition(self, new_status, actor, delivery_partner=None):
        if new_status not in self.TRANSITIONS.get(self.status, set()): raise ValidationError(f"Cannot change order from {self.status} to {new_status}.")
        role = actor.role
        allowed_roles = {self.Status.CONFIRMED: ("admin",), self.Status.ACCEPTED: ("restaurant_owner", "admin"), self.Status.REJECTED: ("restaurant_owner", "admin"),
            self.Status.PREPARING: ("restaurant_owner", "admin"), self.Status.READY: ("restaurant_owner", "admin"), self.Status.ASSIGNED: ("delivery_partner", "admin"),
            self.Status.PICKED_UP: ("delivery_partner", "admin"), self.Status.ON_THE_WAY: ("delivery_partner", "admin"), self.Status.DELIVERED: ("delivery_partner", "admin"),
            self.Status.CANCELLED: ("customer", "restaurant_owner", "admin")}
        if not actor.is_superuser and role not in allowed_roles.get(new_status, ()): raise ValidationError("Your role cannot perform this transition.")
        if role == "restaurant_owner" and self.restaurant.owner_id != actor.id: raise ValidationError("This order belongs to another restaurant.")
        if role == "customer" and self.customer_id != actor.id: raise ValidationError("This is not your order.")
        if role == "delivery_partner" and new_status != self.Status.ASSIGNED and (not self.delivery_partner or self.delivery_partner.user_id != actor.id): raise ValidationError("This delivery is not assigned to you.")
        if delivery_partner is not None: self.delivery_partner = delivery_partner
        self.status = new_status; now = timezone.now()
        if new_status == self.Status.ACCEPTED: self.accepted_at = now
        elif new_status == self.Status.READY: self.prepared_at = now
        elif new_status == self.Status.PICKED_UP: self.picked_up_at = now
        elif new_status == self.Status.DELIVERED:
            self.delivered_at = now
            if self.payment_method == "cod": self.payment_status = "successful"; self.payment.status = "successful"; self.payment.payment_date = now; self.payment.save()
        elif new_status in (self.Status.CANCELLED, self.Status.REJECTED): self.cancelled_at = now
        self.save()
        OrderStatusEvent.objects.create(order=self, status=new_status, changed_by=actor)
        from notifications.services import notify
        notify(self.customer, f"Order {self.get_status_display()}", f"{self.order_number} is now {self.get_status_display()}.", "order")


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True)
    food_name = models.CharField(max_length=160); quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2); subtotal = models.DecimalField(max_digits=12, decimal_places=2)


class OrderStatusEvent(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_events")
    status = models.CharField(max_length=15, choices=Order.Status.choices); changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ("created_at",)
