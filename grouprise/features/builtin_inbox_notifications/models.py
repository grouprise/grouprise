from django.db import models


class BuiltinInboxNotification(models.Model):
    receiver = models.ForeignKey(
        "gestalten.Gestalt", on_delete=models.CASCADE, related_name="notifications"
    )
