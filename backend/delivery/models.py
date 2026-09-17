from django.conf import settings
from django.db import models
class DeliveryPartner(models.Model):
    class Vehicle(models.TextChoices): BIKE = "bike", "Bike"; SCOOTER = "scooter", "Scooter"; BICYCLE = "bicycle", "Bicycle"
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="delivery_profile")
    phone = models.CharField(max_length=20); profile_photo = models.ImageField(upload_to="delivery/", blank=True)
    vehicle_type = models.CharField(max_length=15, choices=Vehicle.choices, default=Vehicle.BIKE); vehicle_number = models.CharField(max_length=30)
    driving_license_number = models.CharField(max_length=50, unique=True); is_available = models.BooleanField(default=False)
    current_latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    current_longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    def __str__(self): return self.user.email
