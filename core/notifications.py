from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import mail
from django.template import loader
from email import utils as email_utils


class Notification:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_recipient_str(self):
        recipient = self.get_recipient()
        return '{} <{}>'.format(recipient, recipient.user.email)

    def get_recipient_strs(self):
        recipients = self.get_recipients()
        if recipients:
            return ['{} <{}>'.format(r, r.user.email) for r in recipients]
        return [self.get_recipient_str()]

    def get_recipients(self):
        return []

    def get_sender(self):
        return None

    def get_sender_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def get_subject(self):
        return self.subject

    def get_template_name(self):
        from django.apps import apps
        print(apps.get_containing_app_config(type(self)))
        return self.template_name

    def send(self):
        for recipient_str in self.get_recipient_strs():
            subject = self.get_subject()
            site = sites_models.Site.objects.get_current()
            context = self._kwargs.copy()
            context.update({'site': site})
            body = loader.render_to_string(self.get_template_name(), context)
            sender = self.get_sender()
            name = '{} via '.format(sender) if sender else ''
            from_email = '{name}{site} <{email}>'.format(
                    name=name,
                    site=site.name,
                    email=self.get_sender_email())
            date = email_utils.formatdate(localtime=True)
            message = mail.EmailMessage(
                    body=body, from_email=from_email, subject=subject,
                    to=[recipient_str], headers={'Date': date})
            message.send()
