import datetime
from math import log

import django.conf
import django.utils.timezone

from grouprise.core.settings import CORE_SETTINGS

from grouprise.features.content import models as content
from grouprise.features.contributions import models as contributions
from grouprise.features.gestalten import models as gestalten
from grouprise.features.groups import models as groups
from grouprise.features.subscriptions import models as subscriptions


class Gestalt:
    @classmethod
    def score(cls, instance):
        minimum_timestamp = (
            django.utils.timezone.now() - datetime.timedelta(days=CORE_SETTINGS.SCORE_CONTENT_AGE))
        s = 0
        if isinstance(instance, gestalten.Gestalt):
            authored_versions = content.Version.objects.filter(
                    author=instance, time_created__gt=minimum_timestamp)
            authored_contributions = contributions.Contribution.objects.filter(
                    author=instance, time_created__gt=minimum_timestamp)
            for qs in (authored_versions, authored_contributions):
                for authored in qs:
                    s += (authored.time_created - minimum_timestamp).days
        return s


class Group:
    @classmethod
    def score(cls, instance):
        minimum_timestamp = (
            django.utils.timezone.now() - datetime.timedelta(days=CORE_SETTINGS.SCORE_CONTENT_AGE))
        s = 0
        if isinstance(instance, groups.Group):
            num_members = instance.memberships.count()
            num_subscribers = subscriptions.Subscription.objects.filter(group=instance).count()
            for only_public, num_gestalten in ((False, num_members), (True, num_subscribers)):
                ps = 0
                group_versions = content.Version.objects.filter(
                       content__associations__entity_id=instance.id,
                       content__associations__entity_type=instance.content_type,
                       time_created__gt=minimum_timestamp)
                group_comments = contributions.Contribution.objects.filter(
                       content__associations__entity_id=instance.id,
                       content__associations__entity_type=instance.content_type,
                       time_created__gt=minimum_timestamp)
                if only_public:
                    group_versions = group_versions.filter(content__associations__public=True)
                    group_comments = group_comments.filter(content__associations__public=True)
                    group_conversations = []
                else:
                    group_conversations = contributions.Contribution.objects.filter(
                           conversation__associations__entity_id=instance.id,
                           conversation__associations__entity_type=instance.content_type,
                           time_created__gt=minimum_timestamp)
                for qs in (group_versions, group_comments, group_conversations):
                    for group_authored in qs:
                        ps += (group_authored.time_created - minimum_timestamp).days
                if num_gestalten > 0:
                    s += ps * log(num_gestalten) * (10 if only_public else 1)
        return s
