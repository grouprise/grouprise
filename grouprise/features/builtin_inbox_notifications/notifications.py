from typing import Union, Any

from grouprise.features.content.models import Content
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.notifications.notifications import (
    RelatedGestalten,
    BaseNotification,
    BaseNotifications,
)


class BuiltinInboxNotification(BaseNotification):
    def send(
        self, recipient: Union[RelatedGestalten.Audience, Gestalt], **kwargs
    ) -> Any:
        if isinstance(self.instance, Content):
            recipient.notifications.create(created_content=self.instance)
        else:
            recipient.notifications.create(created_contribution=self.instance)


class BuiltinInboxNotifications(BaseNotifications):
    notification_class = BuiltinInboxNotification

    def __init__(self, related_gestalten):
        super().__init__(related_gestalten)
        self.recipients_to_ignore.add(self.related_gestalten.author)

    def does_recipient_want_notifications(self, recipient: Gestalt):
        return recipient.receives_builtin_inbox_notifications

    def send(self):
        if self.related_gestalten.is_public_context:
            self.send_to(RelatedGestalten.Audience.GROUP_SUBSCRIBERS)
        else:
            self.send_to(RelatedGestalten.Audience.SUBSCRIBED_GROUP_MEMBERS)
        self.send_to(RelatedGestalten.Audience.ASSOCIATED_GESTALT)
        self.send_to(RelatedGestalten.Audience.EXTERNAL_INITIAL_CONTRIBUTOR)
