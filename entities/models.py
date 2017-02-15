from django.db import models
from features.memberships import models as memberships


class GestaltContent(models.Model):
    content = models.OneToOneField('content.Content')
    gestalt = models.ForeignKey('gestalten.Gestalt')

    def get_unique_id(self):
        return 'gestalt.{}'.format(self.gestalt.id)


class GroupContent(models.Model):
    content = models.OneToOneField('content.Content')
    group = models.ForeignKey('groups.Group')
    pinned = models.BooleanField(default=False)

    def is_external(self):
        return not memberships.Membership.objects.filter(
                group=self.group, member=self.content.author
                ).exists()

    def get_unique_id(self):
        return 'group.{}'.format(self.group.id)
