from django.conf import settings
from django.contrib.sites import models as sites_models
from django.core import mail
from django.template import loader
from email import utils as email_utils


class MembershipCreated:
    def __init__(self, membership):
        recipient = membership.member
        subject = 'Stadtgestalten: In Gruppe aufgenommen'
        to = '{} <{}>'.format(recipient, recipient.user.email)
        body = loader.render_to_string(self.get_template_name())
        from_email = '{site} <{email}>'.format(
                site=sites_models.Site.objects.get_current().name,
                email=settings.DEFAULT_FROM_EMAIL)
        date = email_utils.formatdate(localtime=True)
        message = mail.EmailMessage(
                body=body, from_email=from_email, subject=subject, to=[to],
                headers={'Date': date})
        message.send()

    def get_template_name(self):
        return 'memberships/notifications/membershipcreated.txt'
