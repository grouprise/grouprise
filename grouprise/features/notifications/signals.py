from django.dispatch import receiver

from grouprise.core.signals import post_create
from grouprise.features.email_notifications.signals import send_email_notifications
from grouprise.features.matrix_chat.signals import send_matrix_notifications


@receiver(post_create)
def send_notifications(instance, raw=False, **kwargs):
    if not raw:
        send_email_notifications(instance)
        send_matrix_notifications(instance)
