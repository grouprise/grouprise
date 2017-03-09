from django.contrib.contenttypes import fields as contenttypes
from django.db import models


class ContributionManager(models.Manager):
    def get_by_message_id(self, mid):
        import re
        if mid:
            m = re.match(r'.*\.[0-9]+\.contribution\.([0-9]+)', mid)
            if m:
                return self.get(id=m.group(1))
        raise self.model.DoesNotExist


class Contribution(models.Model):
    container = contenttypes.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey('contenttypes.ContentType', related_name='+')

    contribution = contenttypes.GenericForeignKey('contribution_type', 'contribution_id')
    contribution_id = models.PositiveIntegerField()
    contribution_type = models.ForeignKey('contenttypes.ContentType', related_name='+')

    author = models.ForeignKey('gestalten.Gestalt')
    in_reply_to = models.ForeignKey('Contribution', null=True)
    time_created = models.DateTimeField(auto_now_add=True)

    objects = ContributionManager()

    class Meta:
        ordering = ('time_created',)

    def get_unique_id(self):
        return '{}.{}.contribution.{}'.format(self.container_type, self.container.id, self.id)


class Text(models.Model):
    text = models.TextField()


class ReplyKey(models.Model):
    gestalt = models.ForeignKey('gestalten.Gestalt')
    key = models.CharField(max_length=15, unique=True)
    contribution = models.ForeignKey('Contribution')
    time_created = models.DateTimeField(auto_now_add=True)
