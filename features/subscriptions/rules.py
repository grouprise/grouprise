"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

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

from . import filters, models
from features.memberships import rules as memberships
import rules


@rules.predicate
def has_all_content_unsubscription_for(user, group):
    return models.Unsubscription.objects.filter(
            filters__filter_id=filters.all_content.filter_id,
            subscribed_to=group,
            subscriber=user.gestalt,
            ).exists()


@rules.predicate
def has_external_content_unsubscription_for(user, group):
    return models.Unsubscription.objects.filter(
            filters__filter_id=filters.initial_author_no_member.filter_id,
            subscribed_to=group,
            subscriber=user.gestalt,
            ).exists()


@rules.predicate
def is_subscribed_to(user, instance):
    return models.Subscription.objects.filter(
            subscribed_to=instance,
            subscriber=user.gestalt,
            unsubscribe=False,
            ).exists()


@rules.predicate
def is_subscriber(user, subscription):
    if subscription:
        return (
                not subscription.unsubscribe
                and subscription.subscriber == user.gestalt)
    return False


# rules.add_perm(
#         'subscriptions.create_content_subscription',
#         ~rules.is_authenticated
#         | (rules.is_authenticated
#            & content.is_permitted
#            & ~content.is_author
#            & ~content.is_recipient
#            & ~associations.is_member_of_any_content_group
#            & ~is_subscribed_to))

rules.add_perm(
        'subscriptions.create_all_content_unsubscription',
        rules.is_authenticated
        & memberships.is_member_of
        & ~has_all_content_unsubscription_for)

rules.add_perm(
        'subscriptions.create_external_content_unsubscription',
        rules.is_authenticated
        & memberships.is_member_of
        & ~has_external_content_unsubscription_for)

rules.add_perm(
        'subscriptions.create_group_subscription',
        ~rules.is_authenticated
        | (rules.is_authenticated
           & ~memberships.is_member_of
           & ~is_subscribed_to
           & rules.always_allow))

rules.add_perm(
        'subscriptions.delete_subscription',
        rules.is_authenticated
        & is_subscriber)
