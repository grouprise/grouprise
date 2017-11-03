import os

import django

from core import notifications
from features.conversations import models as conversations
from features.contributions import models as contributions
from features.memberships import models as memberships
from features.gestalten import models as gestalten
from features.groups.models import Group
import core.notifications


def update_recipients(recipients_dict, association=None, subscriptions=[], contributions=[]):
    def update_attributes(key, **kwargs):
        attributes = recipients_dict.setdefault(key, {})
        attributes.update((k, v) for k, v in kwargs.items() if v)

    for subscription in subscriptions:
        membership = subscription.subscriber.memberships \
                .filter(group=subscription.subscribed_to).first()
        update_attributes(
                subscription.subscriber, association=association, membership=membership,
                subscription=subscription)
    for contribution in contributions:
        update_attributes(contribution.author, contribution=contribution)
    if association and not association.entity.is_group:
        update_attributes(association.entity, association=association)
