from itertools import chain
from typing import Any, Iterable, Union

from grouprise.core.templatetags.defaultfilters import full_url
from grouprise.features.content.models import Content
from grouprise.features.contributions.models import Contribution
from grouprise.features.conversations.models import Conversation
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group
from grouprise.features.notifications.notifications import (
    RelatedGestalten,
    BaseNotification,
    BaseNotifications,
)
from . import MatrixMessage
from .settings import MATRIX_SETTINGS
from .utils import (
    send_matrix_messages,
    send_private_message_to_gestalt,
)


def get_matrix_messages_for_public(text: str) -> Iterable[MatrixMessage]:
    for room_id in MATRIX_SETTINGS.PUBLIC_LISTENER_ROOMS:
        yield MatrixMessage(room_id, text)


def get_matrix_messages_for_group(
    group: Group, text: str, is_public: bool
) -> Iterable[MatrixMessage]:
    """return a generator of MatrixMessage instances for the given group

    Zero or more MatrixMessage instances can be returned - based the Matrix rooms of the group and
    the "is_public" flag.

    @param group: the target group for the message
    @param text: the message to be sent
    @param is_public: the public attribute of the source content or contribution
    """
    for room in group.matrix_rooms.all():
        # send private messages only to the internal room
        if is_public or room.is_private:
            yield MatrixMessage(room.room_id, text)
    for room_id in MATRIX_SETTINGS.PUBLIC_LISTENER_ROOMS:
        yield MatrixMessage(room_id, text)


class MatrixNotification(BaseNotification):
    def __init__(self, instance: Union[Content, Contribution]):
        super().__init__(instance)
        if isinstance(self.instance, Content):
            self.is_public = self.association.public
        else:
            self.is_public = self.instance.is_public_in_context_of(
                self.association.entity
            )
        self.context = f"[{self.association.entity}] "
        self.summary = self._get_summary()

    def send(
        self, recipients: Union[RelatedGestalten.Audience, Gestalt], **kwargs
    ) -> Any:
        """assemble and return matrix messages

        The messages are not sent right away.
        Instead we expect, that the messages are collected and sent in a single transaction.

        The incoming `recipients` may be either a Gestalt iterable or one of the target audiences
        mentioned in `bulk_audiences`.
        """
        if recipients == RelatedGestalten.Audience.GROUP_MEMBERS:
            return get_matrix_messages_for_group(
                self.association.entity, self.summary, self.is_public
            )
        elif recipients == RelatedGestalten.Audience.PUBLIC:
            return get_matrix_messages_for_public(self.context + self.summary)
        else:
            send_private_message_to_gestalt(self.context + self.summary, recipients)
            return []

    def _get_summary(self) -> str:
        if isinstance(self.instance, Content):
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
        else:
            if isinstance(self.container, Conversation):
                content_type = "Nachricht"
            else:
                content_type = "Kommentar"
        url = full_url(self.association.get_absolute_url())
        if isinstance(self.instance, Contribution):
            url += f"#contribution-{self.instance.pk}"
        return f"{content_type}: [{self.container.subject}]({url})"


class MatrixNotifications(BaseNotifications):
    bulk_audiences = [
        RelatedGestalten.Audience.GROUP_MEMBERS,
        RelatedGestalten.Audience.PUBLIC,
    ]
    notification_class = MatrixNotification

    def __init__(self, related_gestalten):
        super().__init__(related_gestalten)
        self.recipients_to_ignore.add(self.related_gestalten.author)

    def commit(self):
        send_matrix_messages(
            list(chain.from_iterable(self.results)), "matrix notification"
        )

    def does_recipient_want_notifications(self, recipient: Gestalt):
        return recipient.receives_matrix_notifications

    def send(self):
        self.send_to(RelatedGestalten.Audience.GROUP_MEMBERS)
        if self.related_gestalten.is_public_context:
            if isinstance(self.related_gestalten.instance, Content):
                self.send_to(RelatedGestalten.Audience.PUBLIC)
            self.send_to(RelatedGestalten.Audience.GROUP_SUBSCRIBERS)
        self.send_to(RelatedGestalten.Audience.ASSOCIATED_GESTALT)
        self.send_to(RelatedGestalten.Audience.EXTERNAL_INITIAL_CONTRIBUTOR)
        self.commit()
