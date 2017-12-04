import core
from core import tests
from core.tests import get_url as u
from features.gestalten import tests as gestalten
from features.groups.tests import mixins as groups
from features.memberships import test_mixins as memberships


class GroupRecommend(gestalten.GestaltMixin, groups.GroupMixin, tests.Test):
    def test_group_recommend(self):
        self.client.post(
                self.get_url('group-recommend', self.group.pk),
                {'recipient_email': self.gestalt.user.email})
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)


class MemberInvite(memberships.AuthenticatedMemberMixin, tests.Test):
    def test_member_invite(self):
        r = self.client.post(
                u('member-invite', self.group.pk),
                data={'recipient_email': self.gestalt.user.email})
        self.assertRedirects(r, self.group.get_absolute_url())
        self.assertNotificationSent()
        self.assertNotificationRecipient(self.gestalt)


class TestUrls(core.tests.Test):
    def test_sharing_404(self):
        # r = self.client.get(self.get_url('member-invite', 0))
        # self.assertEqual(r.status_code, 404)
        r = self.client.get(self.get_url('group-recommend', 0))
        self.assertEqual(r.status_code, 404)
