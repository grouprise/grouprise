from grouprise.features.notifications.signals import register_notification_backend
from .notifications import BuiltinInboxNotifications


register_notification_backend(BuiltinInboxNotifications)
