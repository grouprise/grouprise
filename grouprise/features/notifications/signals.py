from typing import Union

from django.dispatch import receiver
from huey.contrib.djhuey import db_task

from grouprise.core.settings import CORE_SETTINGS
from grouprise.core.signals import post_create
from grouprise.features.associations.models import Association
from grouprise.features.builtin_notifications.signals import send_builtin_notifications
from grouprise.features.content.models import Content
from grouprise.features.contributions.models import Contribution
from grouprise.features.conversations.models import Conversation
from grouprise.features.email_notifications.notifications import (
    ContentCreated,
    ContributionCreated,
)
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.matrix_chat.signals import send_matrix_notifications


class AffectedGestalten:
    def __init__(self, instance: Union[Content, Contribution]):
        self.instance = instance
        self.container: Union[Content, Conversation] = (
            instance if isinstance(instance, Content) else instance.container
        )
        self.association: Association = self.container.associations.get()
        self.is_group_context = isinstance(self.association.entity, Group)
        self.gestalten = self._get_affected_gestalten()

    def __contains__(self, item):
        return self.gestalten.__contains__(item)

    def __getitem__(self, item):
        return self.gestalten[item]

    def __iter__(self):
        return self.gestalten["all"].__iter__()

    def get_initial_contributor(self):
        if not self.container.contributions.exists():
            return None
        return self.container.contributions.first().author

    def _get_affected_gestalten(self):
        gestalten = {}
        initial_contributor = self.get_initial_contributor()
        if initial_contributor:
            gestalten["initial_contributor"] = {initial_contributor}
        if self.is_group_context:
            gestalten.update(
                {
                    "group_subscribers": self.association.entity.subscribers.all(),
                    "subscribed_group_members": self.association.entity.members.filter(
                        subscriptions__group=self.association.entity
                    ),
                }
            )
        else:
            gestalten.update(
                {
                    "associated_gestalt": {self.association.entity},
                }
            )
        return {
            "all": {g for subset in gestalten.values() for g in subset},
            **gestalten,
        }


class EmailNotifications:
    def __init__(self, affected_gestalten: AffectedGestalten):
        self.affected_gestalten = affected_gestalten
        if isinstance(self.affected_gestalten.instance, Content):
            self.notification_class = ContentCreated
        else:
            self.notification_class = ContributionCreated
        self.recipients_to_ignore = set()
        try:
            self.recipients_to_ignore.add(
                Gestalt.objects.get(id=CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID)
            )
        except Gestalt.DoesNotExist:
            pass

    def send(self):
        kwargs = {"association": self.affected_gestalten.association}
        if self.affected_gestalten.association.public:
            self.send_to("group_subscribers", is_subscriber=True, **kwargs)
        else:
            if self.affected_gestalten.is_group_context:
                self.send_to("subscribed_group_members", is_subscriber=True, **kwargs)
            else:
                self.send_to("associated_gestalt", **kwargs)
            if self._is_initial_contributor_external():
                self.send_to("initial_contributor", **kwargs)

    def send_to(self, audience_key: str, **kwargs):
        if audience_key in self.affected_gestalten:
            for recipient in self.affected_gestalten[audience_key]:
                if recipient not in self.recipients_to_ignore:
                    self.send_notification(recipient, **kwargs)
                    self.recipients_to_ignore.add(recipient)

    def send_notification(self, recipient, **kwargs):
        self.notification_class(self.affected_gestalten.instance).send(
            recipient, **kwargs
        )

    def _is_initial_contributor_external(self):
        contributor = self.affected_gestalten.get_initial_contributor()
        if self.affected_gestalten.is_group_context:
            members = self.affected_gestalten.association.entity.members.all()
        else:
            members = {self.affected_gestalten.association.entity}
        return contributor and contributor not in members


@receiver(post_create)
def send_notifications(instance, raw=False, **_):
    if not raw:
        _send_notifications(instance)


@db_task()
def _send_notifications(instance):
    affected_gestalten = AffectedGestalten(instance)
    send_builtin_notifications(instance)
    EmailNotifications(affected_gestalten).send()
    send_matrix_notifications(instance)
