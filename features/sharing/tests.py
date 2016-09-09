from core import tests
from features.gestalten import tests as gestalten
from features.groups import tests as groups


class GroupRecommend(gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    def test_recommend(self):
        self.client.post(
                self.get_url('group-recommend', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)


class MemberInvite(gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    def test_recommend(self):
        self.client.post(
                self.get_url('member-invite', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)
