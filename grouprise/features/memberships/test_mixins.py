import grouprise.features.gestalten.tests
import grouprise.features.gestalten.tests.mixins
from grouprise.features.groups.tests.mixins import GroupMixin

from . import models


class MemberMixin(grouprise.features.gestalten.tests.mixins.GestaltMixin, GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
            created_by=cls.gestalt, group=cls.group, member=cls.gestalt
        )


class OtherMemberMixin(
    grouprise.features.gestalten.tests.mixins.OtherGestaltMixin, GroupMixin
):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
            created_by=cls.other_gestalt, group=cls.group, member=cls.other_gestalt
        )


class AuthenticatedMemberMixin(MemberMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.gestalt.user)


class OtherAuthenticatedMemberMixin(OtherMemberMixin):
    def setUp(self):
        super().setUp()
        self.client.force_login(self.other_gestalt.user)
