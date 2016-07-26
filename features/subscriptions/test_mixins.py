from . import models
from utils import tests


class GroupSubscribedMixin(tests.AuthenticatedMixin, tests.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Subscription.objects.create(
                subscribed_to=cls.group, subscriber=cls.gestalt)
