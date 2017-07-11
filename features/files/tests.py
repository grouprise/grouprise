import os
import shutil

import django
import django_mailbox

import core
from features.memberships import test_mixins as memberships


class GroupMessageMixin(memberships.MemberMixin):
    def setUp(self):
        mailbox = django_mailbox.models.Mailbox.objects.create(name='Test')
        self.message = django_mailbox.models.Message.objects.create(
                mailbox=mailbox,
                from_header=self.gestalt.user.email,
                to_header='{}@localhost'.format(self.group.slug),
                body='Text A')


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
