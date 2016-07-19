from .. import models
from django import template

register = template.Library()


@register.filter
def is_subscriber(gestalt, instance):
    return models.Subscription.objects.filter(
            subscribed_to=instance, subscriber=gestalt).exists()


@register.filter
def num_subscriptions(instance):
    return models.Subscription.objects.filter(subscribed_to=instance).count()


@register.filter
def subscription(gestalt, instance):
    return models.Subscription.objects.filter(
            subscribed_to=instance, subscriber=gestalt or None).first()
