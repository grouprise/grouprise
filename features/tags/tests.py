from django.core import mail
from django.core.urlresolvers import reverse
from django_mailbox.models import Message
from django_mailbox.signals import message_received

import core
from core.tests import get_url as u
from features.associations.models import Association
from features.memberships import test_mixins as memberships


class Test(memberships.AuthenticatedMemberMixin, core.tests.Test):

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
        self.assertTrue(self.group.tags.filter(tag__slug='test').exists())

    def test_receive_conversation_contribution_with_tag_by_mail(self):
        # create incoming mail with tag (#302)
        self.client.post(
                reverse('create-group-conversation', args=(self.group.pk,)),
                {'subject': 'Subject', 'text': 'Text'})
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = Message(
                from_header=self.gestalt.user.email,
                body='Delivered-To: {}\n\nText with #tag'.format(reply_to))
        message_received.send(self, message=msg)

    def test_receive_content_contribution_with_tag_by_mail(self):
        # create incoming mail with tag (#302)
        self.client.post(
                reverse('create-group-article', args=(self.group.slug,)),
                {'title': 'Test', 'text': 'Test'})
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = Message(
                from_header=self.gestalt.user.email,
                body='Delivered-To: {}\n\nText with #tag'.format(reply_to))
        message_received.send(self, message=msg)

        # check, that tag page contains link to article
        r = self.client.get(reverse('tag', args=('tag',)))
        self.assertContains(r, 'href="{}"'.format(
            Association.objects.get(content__title='Test').get_absolute_url()))
