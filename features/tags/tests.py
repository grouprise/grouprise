import core
from core.tests import get_url as u
from features.memberships import test_mixins as memberships


class Test(memberships.AuthenticatedMemberMixin, core.tests.Test):

    def test_tag_page_has_group_tag_link(self):
        r = self.client.get(u('tag', 'test'))
        self.assertContainsLink(r, u('tag-group', 'test'))

    def test_tag_group_renders_ok(self):
        r = self.client.get(u('tag-group', 'test'))
        self.assertEqual(r.status_code, 200)

    def test_tag_group_redirects_to_tag_page(self):
        r = self.client.post(u('tag-group', 'test'), data={'group': self.group.id})
        self.assertRedirects(r, u('tag', 'test'))

    def test_tag_group_tags_group(self):
        self.client.post(u('tag-group', 'test'), data={'group': self.group.id})
        self.assertTrue(self.group.tags.filter(tag__slug='test').exists())
