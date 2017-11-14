import os
import shutil

import django
import django_mailbox

import core
from features.associations import models as associations
from features.images import tests as images
from features.memberships import test_mixins as memberships


class GroupMessageMixin(memberships.MemberMixin):
    def setUp(self):
        mailbox = django_mailbox.models.Mailbox.objects.create(name='Test')
        self.message = django_mailbox.models.Message.objects.create(
                mailbox=mailbox,
                from_header=self.gestalt.user.email,
                body='Delivered-To: {}@localhost\n\nText A'.format(self.group.slug))


class GroupMessageWithAttachmentMixin(GroupMessageMixin):
    def setUp(self):
        super().setUp()
        test_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'images', 'tests', 'test.png')
        shutil.copy(test_file, django.conf.settings.MEDIA_ROOT)
        self.message.attachments.create(
                document='./test.png', headers='Content-Type: image/png')


class SendFileByEmail(GroupMessageWithAttachmentMixin, core.tests.Test):
    def test_send_file_by_email(self):
        django_mailbox.signals.message_received.send(self, message=self.message)
        self.assertNotificationSent()
        self.assertEqual(len(django.core.mail.outbox[0].attachments), 1)


class Guest(images.ImageMixin, memberships.MemberMixin, core.tests.Test):
    def create_group_file(self, **kwargs):
        self.client.force_login(self.gestalt.user)
        kwargs.update({'title': 'Group File', 'text': 'Test', 'file': self.image.file})
        self.client.post(self.get_url('create-group-file', self.group.slug), kwargs)
        self.client.logout()

    def get_group_file_url(self):
        return associations.Association.objects.get(
                content__title='Group File').get_absolute_url()

    def test_guest_create_group_file(self):
        self.assertLogin(url_name='create-group-file', url_args=[self.group.slug])
        self.assertLogin(
                url_name='create-group-file', url_args=[self.group.slug], method='post')

    def test_guest_public_group_file(self):
        self.create_group_file(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_file_url())
        self.assertOk(url=self.get_group_file_url())
        self.assertLogin(url=self.get_group_file_url(), method='post')

    def test_guest_internal_group_file(self):
        self.create_group_file(public=False)
        self.assertNotContainsLink(obj=self.group, link_url=self.get_group_file_url())
        self.assertLogin(url=self.get_group_file_url())
        self.assertLogin(url=self.get_group_file_url(), method='post')


class Gestalt(images.ImageMixin, memberships.AuthenticatedMemberMixin, core.tests.Test):
    def create_group_file(self, **kwargs):
        kwargs.update({'title': 'Group File', 'text': 'Test', 'file': self.image.file})
        return self.client.post(self.get_url('create-group-file', self.group.slug), kwargs)

    def get_group_file_url(self):
        return associations.Association.objects.get(
                content__title='Group File').get_absolute_url()

    def test_gestalt_create_group_file(self):
        self.assertEqual(self.client.get(self.get_url(
            'create-group-file', self.group.slug)).status_code, 200)
        response = self.create_group_file()
        self.assertRedirects(response, self.get_group_file_url())
        self.assertExists(associations.Association, content__title='Group File')

    def test_gestalt_public_group_file(self):
        self.create_group_file(public=True)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_file_url())
        self.assertOk(url=self.get_group_file_url())

    def test_gestalt_internal_group_file(self):
        self.create_group_file(public=False)
        self.assertContainsLink(obj=self.group, link_url=self.get_group_file_url())
        self.assertOk(url=self.get_group_file_url())


class TestUrls(core.tests.Test):
    def test_files_404(self):
        r = self.client.get(self.get_url('create-group-file', 'non-existent'))
        self.assertEqual(r.status_code, 404)
