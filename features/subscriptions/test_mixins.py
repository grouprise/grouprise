from . import models
from entities import models as entities
from features.content import tests as content
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class ContentSubscribedMixin(content.NoAuthorContentMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.content, subscriber=cls.gestalt)


class GroupSubscribedMixin(gestalten.AuthenticatedMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt)


class OtherContentSubscriberMixin(
        content.ContentMixin, gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.content,
                subscriber=cls.other_gestalt)


class OtherGroupSubscriberMixin(
        gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group,
                subscriber=cls.other_gestalt)


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


class SenderIsAnonymous:
    def test_sender_name(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSenderAnonymous()


class SenderNameIsGestalt:
    def test_sender_name(self):
        entities.GroupContent.objects.create(
                content=self.content, group=self.group)
        self.assertNotificationSenderName(self.gestalt)
