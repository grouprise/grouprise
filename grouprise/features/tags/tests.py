from django.core import mail
from django.urls import reverse

from grouprise.core.tests import Test, get_url as u
from grouprise.features.associations.models import Association
from grouprise.features.groups.tests.mixins import GroupMixin
from grouprise.features.imports.tests.test_mail import MailInjectLMTPMixin
from grouprise.features.memberships.test_mixins import AuthenticatedMemberMixin


class TaggedGroupMixin(GroupMixin):
    def setUp(self):
        super().setUp()
        self.group.tags.add('test')


class BasicTagTests(AuthenticatedMemberMixin, MailInjectLMTPMixin, Test):

    def test_tag_page_has_group_tag_link(self):
        self.client.get(u('tag', 'test'))
        # self.assertContainsLink(r, u('tag-group', 'test'))

    def test_tag_group_renders_ok(self):
        r = self.client.get(u('tag-group', 'test'))
        self.assertEqual(r.status_code, 200)

    def test_tag_group_redirects_to_tag_page(self):
        r = self.client.post(u('tag-group', 'test'), data={'group': self.group.id})
        self.assertRedirects(r, u('tag', 'test'))

    def test_tag_group_tags_group(self):
        self.client.post(u('tag-group', 'test'), data={'group': self.group.id})
        self.assertTrue(self.group.tags.filter(slug='test').exists())

    def test_receive_conversation_contribution_with_tag_by_mail(self):
        # create incoming mail with tag (#302)
        self.client.post(
                reverse('create-group-conversation', args=(self.group.pk,)),
                {'subject': 'Subject', 'text': 'Text'})
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        self.inject_mail(self.gestalt.user.email, [reply_to], data='Text with #tag')

    def test_receive_content_contribution_with_tag_by_mail(self):
        # create incoming mail with tag (#302)
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test'})
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        self.inject_mail(self.gestalt.user.email, [reply_to], data='Text with #tag')

        # check, that tag page contains link to article
        r = self.client.get(reverse('tag', args=('tag',)))
        self.assertContains(r, 'href="{}"'.format(
            Association.objects.get(content__title='Test').get_absolute_url()))


class TaggedGroupTests(TaggedGroupMixin, AuthenticatedMemberMixin, Test):
    def test_show_settings_page(self):
        r = self.client.get('{}?group={}'.format(reverse('group-settings'), self.group.slug))
        self.assertEqual(r.status_code, 200)
