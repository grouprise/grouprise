from django.contrib.contenttypes import (
        fields as contenttypes_fields, models as contenttypes_models)
from django.db import models
from django.utils import timezone
import re


class ReplyKey(models.Model):
    gestalt = models.ForeignKey('gestalten.Gestalt')
    key = models.CharField(max_length=15, unique=True)
    text = models.ForeignKey('Text')
    time_created = models.DateTimeField(auto_now_add=True)


class TextManager(models.Manager):
    def get_by_message_id(self, mid):
        m = re.match(r'.*\.[0-9]+\.text\.([0-9]+)', mid)
        if m:
            return self.get(id=m.group(1))
        else:
            raise self.model.DoesNotExist


class Text(models.Model):
    container = contenttypes_fields.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(contenttypes_models.ContentType)

    author = models.ForeignKey('gestalten.Gestalt', related_name='texts')
    in_reply_to = models.ForeignKey('Text', null=True, related_name='+')
    time_created = models.DateTimeField(default=timezone.now)
    text = models.TextField()

    objects = TextManager()

    class Meta:
        ordering = ('time_created',)

    def get_unique_id(self):
        return '{}.{}.text.{}'.format(self.container_type, self.container.id, self.id)
