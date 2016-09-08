from utils import tests


class GroupRecommend(tests.GestaltMixin, tests.GroupMixin, tests.Test):
    def test_recommend(self):
        self.client.post(
                self.get_url('group-recommend', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)


class MemberInvite(tests.GestaltMixin, tests.GroupMixin, tests.Test):
    def test_recommend(self):
        self.client.post(
                self.get_url('member-invite', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)
