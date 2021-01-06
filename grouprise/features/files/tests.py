import contextlib
import os
import unittest
import tempfile

import django

import grouprise.core.tests
from grouprise.features.associations import models as associations
from grouprise.features.files.models import get_unique_storage_filename
from grouprise.features.images import tests as images
from grouprise.features.imports.tests.test_mail import GroupMailMixin, MailInjectLMTPMixin
from grouprise.features.memberships import test_mixins as memberships


class MessageWithAttachmentMixin(MailInjectLMTPMixin):
    def setUp(self):
        super().setUp()
        test_file = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'images', 'tests', 'test.png')
        with open(test_file, 'rb') as test_file_handle:
            test_file_raw = test_file_handle.read()
        self.message = self.assemble_mail_data(
                {}, body='Text A',
                attachments=[{
                    'content_type': 'image/png',
                    'payload': test_file_raw,
                    'disposition_filename': './test.png'}])


class SendFileByEmail(MessageWithAttachmentMixin, GroupMailMixin, grouprise.core.tests.Test):
    def test_send_file_by_email(self):
        self.inject_mail(self.gestalt.user.email, [self.group_address], self.message)
        self.assertNotificationSent()
        self.assertEqual(len(django.core.mail.outbox[0].attachments), 1)


class Guest(images.ImageMixin, memberships.MemberMixin, grouprise.core.tests.Test):
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


class Gestalt(images.ImageMixin, memberships.AuthenticatedMemberMixin, grouprise.core.tests.Test):
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


class FilenameGenerator(unittest.TestCase):

    def setUp(self):
        self._base_dir = tempfile.mkdtemp()
        # Manage a set of created filenames.  Otherwise the 'tearDown' method preempts the context
        # cleanup and thus fails to remove the temporary directory.
        self._filenames = set()
        super().setUp()

    def tearDown(self):
        for filename in self._filenames:
            os.unlink(filename)
        os.rmdir(self._base_dir)

    @contextlib.contextmanager
    def get_unique_filename(self, name_template, default_prefix=None):
        filename = get_unique_storage_filename(name_template, self._base_dir,
                                               default_prefix=default_prefix)
        self._filenames.add(filename)
        yield filename
        os.unlink(filename)
        self._filenames.remove(filename)

    def test_unique_name_generator(self):
        with self.get_unique_filename('foo.bar.baz', 'nom') as filename:
            self.assertEqual(os.path.dirname(filename), self._base_dir)
            self.assertTrue(os.path.basename(filename))
            self.assertTrue(os.path.basename(filename).startswith('foo.bar-'), filename)
            self.assertTrue(os.path.basename(filename).endswith('.baz'), filename)
        with self.get_unique_filename(None, 'foo-') as filename:
            self.assertEqual(os.path.dirname(filename), self._base_dir)
            self.assertTrue(os.path.basename(filename))
            self.assertTrue(os.path.basename(filename).startswith('foo-'), filename)
            self.assertNotIn('.', os.path.basename(filename))


class TestUrls(grouprise.core.tests.Test):
    def test_files_404(self):
        r = self.client.get(self.get_url('create-group-file', 'non-existent'))
        self.assertEqual(r.status_code, 404)
