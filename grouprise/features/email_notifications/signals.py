from grouprise.features.notifications.signals import register_notification_backend
from .notifications import EmailNotifications


register_notification_backend(EmailNotifications)