from django.urls import path
from .views import AcceptDeliveryView, AssignedDeliveriesView, AvailableDeliveriesView, EarningsView, ProfileView
urlpatterns = [path("delivery/profile/", ProfileView.as_view()), path("delivery/available/", AvailableDeliveriesView.as_view()),
    path("delivery/assigned/", AssignedDeliveriesView.as_view()), path("delivery/<int:pk>/accept/", AcceptDeliveryView.as_view()),
    path("delivery/earnings/", EarningsView.as_view())]
