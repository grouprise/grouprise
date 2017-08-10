from django.contrib.contenttypes import fields as contenttypes
from django.db import models

from . import querysets


class Membership(models.Model):
    class Meta:
        unique_together = ('group', 'member')

    created_by = models.ForeignKey(
            'gestalten.Gestalt', related_name='memberships_created')
    date_joined = models.DateField(auto_now_add=True)
    group = models.ForeignKey('groups.Group', related_name='memberships')
    member = models.ForeignKey('gestalten.Gestalt', related_name='memberships')

    objects = models.Manager.from_queryset(querysets.MembershipQuerySet)()

    def __str__(self):
        return "%s is member of %s since %s" % (
            str(self.member.user.get_username()),
            str(self.group.slug), str(self.date_joined)
        )


class Application(models.Model):
    group = models.ForeignKey('groups.Group', related_name='applications')

    contributions = contenttypes.GenericRelation(
            'contributions.Contribution',
            content_type_field='contribution_type',
            object_id_field='contribution_id',
            related_query_name='membership_application')

    @property
    def contribution(self):
        return self.contributions.first()
