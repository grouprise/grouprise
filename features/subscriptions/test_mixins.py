from . import models
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class GroupSubscribedMixin(gestalten.AuthenticatedMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt)


class OtherGroupSubscriberMixin(
        gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group,
                subscriber=cls.other_gestalt)
