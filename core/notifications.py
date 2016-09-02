from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import mail
from django.template import loader
from email import utils as email_utils


class Notification:
    def __init__(self, **kwargs):
        self._kwargs = kwargs
        for k, v in kwargs.items():
            setattr(self, k, v)

    def get_recipient_str(self):
        recipient = self.get_recipient()
        return '{} <{}>'.format(recipient, recipient.user.email)

    def get_subject(self):
        return self.subject

    def get_template_name(self):
        return self.template_name

    def send(self):
        subject = self.get_subject()
        site = sites_models.Site.objects.get_current()
        to = self.get_recipient_str()
        context = self._kwargs.copy()
        context.update({'site': site})
        body = loader.render_to_string(self.get_template_name(), context)
        from_email = '{site} <{email}>'.format(
                site=site.name,
                email=settings.DEFAULT_FROM_EMAIL)
        date = email_utils.formatdate(localtime=True)
        message = mail.EmailMessage(
                body=body, from_email=from_email, subject=subject, to=[to],
                headers={'Date': date})
        message.send()
