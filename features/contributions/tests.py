import django
from django.core import mail
from django.core.urlresolvers import reverse
from django_mailbox import models as mailbox_models, signals as mailbox_signals

import features.articles.tests
from core import tests
from features.associations import models as associations
from features.gestalten import tests as gestalten
from features.memberships import test_mixins as memberships
from . import models


class ContributionMixin(features.articles.tests.ArticleMixin):
    def create_contribution(self):
        self.client.post(
                reverse('content', args=[self.association.entity.slug, self.association.slug]),
                {'text': 'Test Comment'})
        return models.Contribution.objects.get(text__text='Test Comment')

    def setUp(self):
        super().setUp()
        self.contribution = self.create_contribution()


class ContentReplyByEmail(
        gestalten.AuthenticatedMixin, tests.Test):
    def test_content_reply_by_email(self):
        # create article
        self.client.post(self.get_url('create-article'), {'title': 'Test', 'text': 'Test'})
        a = self.assertExists(associations.Association, content__title='Test')
        self.assertNotificationSent()
        # generate reply message
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = mailbox_models.Message(to_header=reply_to, body='Text B')
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(
                models.Contribution, content=a.content.get(),
                text__text='Text B')


class ConversationInitiateByEmail(memberships.MemberMixin, tests.Test):
    def test_conversation_initiate_by_email(self):
        # generate initial message
        msg = mailbox_models.Message(
                from_header=self.gestalt.user.email,
                to_header='{}@localhost'.format(self.group.slug),
                body='Text A')
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(
                models.Contribution, conversation__associations__group=self.group,
                text__text='Text A')

    def test_conversation_initiate_by_email_failing(self):
        # generate initial message
        msg = mailbox_models.Message(
                from_header=self.gestalt.user.email, to_header='not-existing@localhost',
                body='Text A')
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertEqual(len(mail.outbox), 1)


class ConversationReplyByEmail(
        gestalten.AuthenticatedMixin, gestalten.OtherGestaltMixin, tests.Test):
    def test_texts_reply_by_email(self):
        # send message to other_gestalt via web interface
        self.client.post(
                self.get_url('create-gestalt-conversation', self.other_gestalt.pk),
                {'subject': 'Subject A', 'text': 'Text A'})
        text_a = self.assertExists(models.Contribution, conversation__subject='Subject A')
        self.assertNotificationSent()
        # generate reply message
        reply_to = mail.outbox[0].extra_headers['Reply-To']
        msg = mailbox_models.Message(to_header=reply_to, body='Text B')
        # send signal like getmail would
        mailbox_signals.message_received.send(self, message=msg)
        self.assertExists(
                models.Contribution, conversation=text_a.conversation.get(),
                text__text='Text B')


class Delete(ContributionMixin, django.test.TestCase):
    def test_delete_association(self):
        delete_url = reverse(
                'delete-contribution',
                args=[
                    self.association.entity.slug, self.association.slug, self.contribution.pk])
        article_url = reverse(
                'content', args=[self.association.entity.slug, self.association.slug])

        # article contains comment
        r = self.client.get(article_url)
        self.assertContains(r, 'Test Comment')

        # find delete link on article page
        self.assertContains(r, 'href="{}"'.format(delete_url))

        # get delete confirmation page
        r = self.client.get(delete_url)
        self.assertEqual(r.status_code, 200)

        # delete comment
        r = self.client.post(delete_url)
        self.assertRedirects(r, article_url)

        # article contains comment
        r = self.client.get(article_url)
        self.assertNotContains(r, 'Test Comment')
