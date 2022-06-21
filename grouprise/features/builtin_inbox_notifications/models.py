from django.db import models


class BuiltinInboxNotificationQuerySet(models.QuerySet):
    def filter_unread(self):
        return self.filter(is_read=False)


class BuiltinInboxNotification(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    created_content = models.ForeignKey(
        "content2.Content",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
    )
    created_contribution = models.ForeignKey(
        "contributions.Contribution",
        on_delete=models.CASCADE,
        related_name="+",
        null=True,
    )
    receiver = models.ForeignKey(
        "gestalten.Gestalt",
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    is_read = models.BooleanField(default=False)

    objects = models.Manager.from_queryset(BuiltinInboxNotificationQuerySet)()

    @property
    def association(self):
        if self.created_content:
            container = self.created_content
        else:
            container = self.created_contribution.container
        return container.associations.get()
