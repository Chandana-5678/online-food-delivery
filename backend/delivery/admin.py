from django.contrib import admin
from .models import DeliveryPartner
@admin.register(DeliveryPartner)
class DeliveryPartnerAdmin(admin.ModelAdmin): list_display = ("user", "vehicle_type", "vehicle_number", "is_available", "rating"); list_filter = ("vehicle_type", "is_available")
