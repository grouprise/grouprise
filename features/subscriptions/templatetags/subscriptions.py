from .. import models
from django import template

register = template.Library()


@register.filter
def num_subscriptions(instance):
    return models.Subscription.objects.filter(subscribed_to=instance).count()


@register.filter
def subscription(instance, user):
    if user.is_authenticated():
        return models.Subscription.objects.filter(subscribed_to=instance, subscriber=user.gestalt).first()
    return None
