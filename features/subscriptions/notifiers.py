from . import models
from entities import models as entities_models


class Subscription:
    def get_recipients_for(instance):
        subscriptions = models.Subscription.objects.filter(
                subscribed_to=instance)
        return entities_models.Gestalt.objects.filter(
                subscription__in=subscriptions)
