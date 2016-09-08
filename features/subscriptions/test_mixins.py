from . import models
from entities import models as entities
from utils import tests


class ContentSubscribedMixin(tests.NoAuthorContentMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.content, subscriber=cls.gestalt)


class GroupSubscribedMixin(tests.AuthenticatedMixin, tests.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt)


class NoNotificationToOtherGestalt:
    def test_associate_content(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNoNotificationSent()


class NotificationToOtherGestalt:
    def test_associate_content(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.other_gestalt)


class OtherGroupSubscriberMixin(tests.OtherGestaltMixin, tests.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group,
                subscriber=cls.other_gestalt)
