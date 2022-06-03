from abc import abstractmethod, ABCMeta
from enum import Enum, auto
from itertools import chain
from typing import Union, Iterable, Iterator, Optional, Mapping, Any

from django.dispatch import receiver
from huey.contrib.djhuey import db_task

from grouprise.core.settings import CORE_SETTINGS
from grouprise.core.signals import post_create
from grouprise.core.templatetags.defaultfilters import full_url
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
from grouprise.features.matrix_chat.signals import (
    send_matrix_messages,
    get_matrix_messages_for_group,
    get_matrix_messages_for_public,
)


class AffectedGestalten:
    class Audience(Enum):
        # all gestalten affected by changes to the given instance
        ALL = auto()
        # the gestalt to whom this content is associated, if any
        ASSOCIATED_GESTALT = auto()
        # the author of the initial contribution, if any
        INITIAL_CONTRIBUTOR = auto()
        # all members of the associated group, if any
        GROUP_MEMBERS = auto()
        # all gestalten who subscribed to the associated group, if any
        GROUP_SUBSCRIBERS = auto()
        # an empty set as a placeholder for the public audience
        PUBLIC = auto()
        # all members of the associated group who have a subscription
        SUBSCRIBED_GROUP_MEMBERS = auto()

    def __init__(self, instance: Union[Content, Contribution]) -> None:
        self.instance = instance
        self.container: Union[Content, Conversation] = (
            instance if isinstance(instance, Content) else instance.container
        )
        self.association: Association = self.container.associations.get()
        self.is_group_context = isinstance(self.association.entity, Group)
        self.gestalten = self._get_affected_gestalten()

    def __contains__(self, item: Audience) -> bool:
        return self.gestalten.__contains__(item)

    def __getitem__(self, item: Audience) -> Iterable[Gestalt]:
        return self.gestalten[item]

    def __iter__(self) -> Iterator[Gestalt]:
        return self.gestalten[self.Audience.ALL].__iter__()

    def get_initial_contributor(self) -> Optional[Gestalt]:
        if not self.container.contributions.exists():
            return None
        return self.container.contributions.first().author

    def _get_affected_gestalten(self) -> Mapping[Audience, Iterable[Gestalt]]:
        gestalten = {
            self.Audience.PUBLIC: {},
        }
        initial_contributor = self.get_initial_contributor()
        if initial_contributor:
            gestalten[self.Audience.INITIAL_CONTRIBUTOR] = {initial_contributor}
        if self.is_group_context:
            gestalten.update(
                {
                    self.Audience.GROUP_MEMBERS: (
                        self.association.entity.members.all()
                    ),
                    self.Audience.GROUP_SUBSCRIBERS: (
                        self.association.entity.subscribers.all()
                    ),
                    self.Audience.SUBSCRIBED_GROUP_MEMBERS: (
                        self.association.entity.members.filter(
                            subscriptions__group=self.association.entity
                        )
                    ),
                }
            )
        else:
            gestalten.update(
                {
                    self.Audience.ASSOCIATED_GESTALT: {self.association.entity},
                }
            )
        return {
            self.Audience.ALL: {g for subset in gestalten.values() for g in subset},
            **gestalten,
        }


class BaseNotification(metaclass=ABCMeta):
    def __init__(self, instance: Union[Content, Contribution]):
        self.instance = instance
        self.container: Union[Content, Conversation] = (
            instance if isinstance(instance, Content) else instance.container
        )
        self.association: Association = self.container.associations.get()

    @abstractmethod
    def send(
        self, recipients: Union[AffectedGestalten.Audience, Gestalt], **kwargs
    ) -> Any:
        pass


class MatrixNotification(BaseNotification):
    def __init__(self, instance: Union[Content, Contribution]):
        super().__init__(instance)
        self.summary = self._get_summary()

    def send(
        self, recipients: Union[AffectedGestalten.Audience, Gestalt], **kwargs
    ) -> Any:
        if recipients == AffectedGestalten.Audience.GROUP_MEMBERS:
            return get_matrix_messages_for_group(
                self.association.entity, self.summary, self.association.public
            )
        elif recipients == AffectedGestalten.Audience.PUBLIC:
            summary = f"[{self.association.entity.name}] {self.summary}"
            return get_matrix_messages_for_public(summary)

    def _get_summary(self):
        if self.instance.is_event:
            content_type = "Termin"
        elif self.instance.is_file:
            content_type = "Anhang"
        elif self.instance.is_gallery:
            content_type = "Galerie"
        elif self.instance.is_poll:
            content_type = "Umfrage"
        elif self.instance.is_conversation:
            content_type = "Gespräch"
        else:
            content_type = "Artikel"
        url = full_url(self.association.get_absolute_url())
        return f"{content_type}: [{self.instance.subject}]({url})"


class BaseNotifications(metaclass=ABCMeta):
    bulk_audiences = []
    notification_class = None

    def __init__(self, affected_gestalten: AffectedGestalten):
        self.affected_gestalten = affected_gestalten
        self.recipients_to_ignore = set()
        try:
            self.recipients_to_ignore.add(
                Gestalt.objects.get(id=CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID)
            )
        except Gestalt.DoesNotExist:
            pass
        self.results = []

    def does_recipient_want_notifications(self, recipient: Gestalt):
        return True

    def get_notification_class(self):
        return self.notification_class

    @abstractmethod
    def send(self):
        pass

    def send_to(self, audience: AffectedGestalten.Audience, **kwargs):
        try:
            recipients = self.affected_gestalten[audience]
            if audience in self.bulk_audiences:
                self.send_notification(audience, **kwargs)
                self.recipients_to_ignore.update(recipients)
            else:
                for recipient in recipients:
                    if (
                        recipient not in self.recipients_to_ignore
                        and self.does_recipient_want_notifications(recipient)
                    ):
                        self.send_notification(recipient, **kwargs)
                        self.recipients_to_ignore.add(recipient)
        except KeyError:
            # we cannot send notifications to a non-existing audience
            pass

    def send_notification(
        self, recipients: Union[AffectedGestalten.Audience, Gestalt], **kwargs
    ):
        notification_class = self.get_notification_class()
        notification = notification_class(self.affected_gestalten.instance)
        result = notification.send(recipients, **kwargs)
        self.results.append(result)


class EmailNotifications(BaseNotifications):
    def does_recipient_want_notifications(self, recipient: Gestalt):
        return not recipient.is_email_blocker

    def get_notification_class(self):
        if isinstance(self.affected_gestalten.instance, Content):
            return ContentCreated
        else:
            return ContributionCreated

    def send(self):
        kwargs = {"association": self.affected_gestalten.association}
        if self.affected_gestalten.association.public:
            self.send_to(
                AffectedGestalten.Audience.GROUP_SUBSCRIBERS,
                is_subscriber=True,
                **kwargs,
            )
        else:
            if self.affected_gestalten.is_group_context:
                self.send_to(
                    AffectedGestalten.Audience.SUBSCRIBED_GROUP_MEMBERS,
                    is_subscriber=True,
                    **kwargs,
                )
            else:
                self.send_to(AffectedGestalten.Audience.ASSOCIATED_GESTALT, **kwargs)
            if self._is_initial_contributor_external():
                self.send_to(AffectedGestalten.Audience.INITIAL_CONTRIBUTOR, **kwargs)

    def _is_initial_contributor_external(self):
        contributor = self.affected_gestalten.get_initial_contributor()
        if self.affected_gestalten.is_group_context:
            members = self.affected_gestalten.association.entity.members.all()
        else:
            members = {self.affected_gestalten.association.entity}
        return contributor and contributor not in members


class MatrixNotifications(BaseNotifications):
    bulk_audiences = [
        AffectedGestalten.Audience.GROUP_MEMBERS,
        AffectedGestalten.Audience.PUBLIC,
    ]
    notification_class = MatrixNotification

    def commit(self):
        send_matrix_messages(
            list(chain.from_iterable(self.results)), "matrix notification"
        )

    def send(self):
        if isinstance(self.affected_gestalten.instance, Content):
            self.send_to(AffectedGestalten.Audience.GROUP_MEMBERS)
            if self.affected_gestalten.association.public:
                self.send_to(AffectedGestalten.Audience.PUBLIC)
        self.commit()


@receiver(post_create)
def send_notifications(instance, raw=False, **_):
    if not raw:
        _send_notifications(instance)


@db_task()
def _send_notifications(instance):
    affected_gestalten = AffectedGestalten(instance)
    send_builtin_notifications(instance)
    EmailNotifications(affected_gestalten).send()
    MatrixNotifications(affected_gestalten).send()
