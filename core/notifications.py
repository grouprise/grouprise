from django.apps import apps
from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import mail
from django.template import loader
from email import utils as email_utils


class Notification:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    @staticmethod
    def format_recipient(gestalt):
        return '{} <{}>'.format(gestalt, gestalt.user.email)

    def get_formatted_recipients(self):
        recipients = self.get_recipients()
        if type(recipients) == dict:
            return [(self.format_recipient(r), with_name)
                    for r, with_name in recipients.items()]
        else:
            return [(self.format_recipient(r), True) for r in recipients]

    def get_sender(self):
        return None

    def get_sender_email(self):
        return settings.DEFAULT_FROM_EMAIL

    def get_subject(self):
        return self.subject

    def get_template_name(self):
        app_label = apps.get_containing_app_config(type(self).__module__).label
        return '{}/{}.txt'.format(
                app_label, type(self).__name__.lower())

    def send(self):
        for recipient, with_name in self.get_formatted_recipients():
            subject = self.get_subject()
            site = sites_models.Site.objects.get_current()
            context = self.kwargs.copy()
            context.update({'site': site})
            body = loader.render_to_string(self.get_template_name(), context)
            sender = self.get_sender()
            name = '{} via '.format(sender) if sender and with_name else ''
            from_email = '{name}{site} <{email}>'.format(
                    name=name,
                    site=site.name,
                    email=self.get_sender_email())
            date = email_utils.formatdate(localtime=True)
            message = mail.EmailMessage(
                    body=body, from_email=from_email, subject=subject,
                    to=[recipient], headers={'Date': date})
            message.send()
