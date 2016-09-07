from content import models as content
from entities import models as entities
from features.memberships import test_mixins as memberships
from utils import tests


class EventMixin:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.content = content.Event.objects.create(
                author=cls.gestalt, time='2000-01-01 12:00+00:00')


class NotificationToOtherGestalt:
    def test_event_create(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class GroupInternalEvent(
        NotificationToOtherGestalt,
        EventMixin, memberships.TwoMembersMixin, tests.Test):
    """
    If a group member creates an event
    * a notification should be sent.
    """
