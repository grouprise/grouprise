"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

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
