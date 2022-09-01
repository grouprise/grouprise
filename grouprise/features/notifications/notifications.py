from abc import ABCMeta, abstractmethod
from enum import Enum, auto
from typing import Union, Iterable, Iterator, Mapping, Any

from grouprise.core.settings import CORE_SETTINGS
from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.contributions.models import Contribution
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group


class RelatedGestalten:
    class Audience(Enum):
        # all gestalten affected by changes to the given instance
        ALL = auto()
        # the gestalt to whom this content is associated, if any
        ASSOCIATED_GESTALT = auto()
        # the author of the initial contribution, if any
        EXTERNAL_INITIAL_CONTRIBUTOR = auto()
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
        if isinstance(instance, Content):
            self.author = instance.versions.last().author
            self.container = instance
        else:
            self.author = instance.author
            self.container = instance.container
        self.association: Association = self.container.associations.get()
        self.entity: Union[Gestalt, Group] = self.association.entity
        self.is_group_context = isinstance(self.entity, Group)
        if isinstance(instance, Content):
            self.is_public_context = self.association.public
        else:
            self.is_public_context = instance.is_public_in_context_of(self.entity)
        self.gestalten = self._get_related_gestalten()

    def __contains__(self, item: Audience) -> bool:
        return self.gestalten.__contains__(item)

    def __getitem__(self, item: Audience) -> Iterable[Gestalt]:
        return self.gestalten[item]

    def __iter__(self) -> Iterator[Gestalt]:
        return self.gestalten[self.Audience.ALL].__iter__()

    def _get_related_gestalten(self) -> Mapping[Audience, Iterable[Gestalt]]:
        gestalten = {
            self.Audience.PUBLIC: {},
        }
        initial_contributor, is_external = self._get_initial_contributor()
        if initial_contributor and is_external:
            gestalten.update(
                {
                    self.Audience.EXTERNAL_INITIAL_CONTRIBUTOR: {initial_contributor},
                }
            )
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

    def _get_initial_contributor(self):
        if not self.container.contributions.exists():
            return None, False
        contributor = self.container.contributions.first().author
        if self.is_group_context:
            members = self.association.entity.members.all()
        else:
            members = {self.association.entity}
        return contributor, contributor not in members


class BaseNotification(metaclass=ABCMeta):
    def __init__(self, instance: Union[Content, Contribution]):
        self.instance = instance
        if isinstance(instance, Content):
            self.container = instance
        else:
            self.container = instance.container
        self.association: Association = self.container.associations.get()

    @abstractmethod
    def send(
        self, recipients: Union[RelatedGestalten.Audience, Gestalt], **kwargs
    ) -> Any:
        pass


class BaseNotifications(metaclass=ABCMeta):
    bulk_audiences = []
    notification_class = None

    def __init__(self, related_gestalten: RelatedGestalten):
        self.related_gestalten = related_gestalten
        notification_class = self.get_notification_class()
        self.notification = notification_class(self.related_gestalten.instance)
        self.results = []
        self.recipients_to_ignore = set()
        try:
            self.recipients_to_ignore.add(
                Gestalt.objects.get(id=CORE_SETTINGS.FEED_IMPORTER_GESTALT_ID)
            )
        except Gestalt.DoesNotExist:
            pass

    def does_recipient_want_notifications(self, recipient: Gestalt):
        return True

    def get_notification_class(self):
        return self.notification_class

    @abstractmethod
    def send(self):
        pass

    def send_to(self, audience: RelatedGestalten.Audience, **kwargs):
        try:
            recipients = self.related_gestalten[audience]
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
        self, recipients: Union[RelatedGestalten.Audience, Gestalt], **kwargs
    ):
        result = self.notification.send(recipients, **kwargs)
        self.results.append(result)
