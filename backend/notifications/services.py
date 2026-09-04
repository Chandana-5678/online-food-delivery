from .models import Notification
def notify(user, title, message, notification_type="order"):
    return Notification.objects.create(user=user, title=title, message=message, notification_type=notification_type)
