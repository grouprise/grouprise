from allauth.account import adapter as allauth_adapter
from django.conf import settings
from django.contrib import auth
from django.core import urlresolvers
from django.db import models
from features.memberships import models as memberships
import randomcolor


class GestaltContent(models.Model):
    content = models.OneToOneField('content.Content')
    gestalt = models.ForeignKey('gestalten.Gestalt')


class GroupContent(models.Model):
    content = models.OneToOneField('content.Content')
    group = models.ForeignKey('groups.Group')
    pinned = models.BooleanField(default=False)

    def is_external(self):
        return not memberships.Membership.objects.filter(
                group=self.group, member=self.content.author
                ).exists()
