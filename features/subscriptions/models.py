import django
from django.db import models


class Subscription(models.Model):
    class Meta:
        unique_together = ('subscribed_to_type', 'subscribed_to_id', 'subscriber')

    # target (e.g. a group)
    subscribed_to_type = models.ForeignKey(
            'contenttypes.ContentType', on_delete=models.CASCADE)
    subscribed_to_id = models.PositiveIntegerField()
    subscribed_to = django.contrib.contenttypes.fields.GenericForeignKey(
            'subscribed_to_type', 'subscribed_to_id')

    # subscriber
    subscriber = models.ForeignKey(
            'gestalten.Gestalt', on_delete=models.CASCADE, related_name='subscriptions')

    def __str__(self):
        return '{} - {}'.format(self.subscribed_to, self.subscriber)
