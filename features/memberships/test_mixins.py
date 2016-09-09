from . import models
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class MemberMixin(gestalten.AuthenticatedMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
                created_by=cls.gestalt, group=cls.group, member=cls.gestalt)


class OtherMemberMixin(gestalten.OtherGestaltMixin, groups.GroupMixin):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        models.Membership.objects.create(
                created_by=cls.other_gestalt,
                group=cls.group,
                member=cls.other_gestalt)
