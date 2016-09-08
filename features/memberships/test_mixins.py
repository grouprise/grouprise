from . import models
from utils import tests


class MemberMixin(tests.AuthenticatedMixin, tests.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
                created_by=cls.gestalt, group=cls.group, member=cls.gestalt)


class OtherMemberMixin(tests.OtherGestaltMixin, tests.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
                created_by=cls.other_gestalt,
                group=cls.group,
                member=cls.other_gestalt)
