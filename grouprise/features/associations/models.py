from django.contrib.contenttypes import fields as contenttypes
from django.db import models

import grouprise.core.models
from . import querysets


class Association(grouprise.core.models.Model):
    pinned = models.BooleanField(
            'Im Intro der Gruppe anheften', default=False,
            help_text='Angeheftete Beiträge werden auf der Gruppenseite zuerst angezeigt. Sie '
            'können beispielsweise für allgemeine Einleitungs- und Beschreibungstexte '
            'verwendet werden.')
    public = models.BooleanField(
            'Öffentlich', default=False,
            help_text='Öffentliche Beiträge sind auch für Besucherinnen sichtbar, die nicht '
            'Mitglied der Gruppe sind. Benachrichtigungen werden an Mitglieder und '
            'Abonnentinnen versendet.')
    slug = models.SlugField(
            'Kurzname', default=None, null=True,
            help_text='Der Kurzname wird beispielsweise in der Webadresse des Beitrags '
            'verwendet.')

    deleted = models.DateTimeField(null=True, blank=True)

    container = contenttypes.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(
            'contenttypes.ContentType', related_name='container_associations',
            on_delete=models.CASCADE)

    entity = contenttypes.GenericForeignKey('entity_type', 'entity_id')
    entity_id = models.PositiveIntegerField()
    entity_type = models.ForeignKey(
            'contenttypes.ContentType', related_name='entity_associations',
            on_delete=models.CASCADE)

    objects = models.Manager.from_queryset(querysets.Association)()

    class Meta:
        unique_together = ('entity_id', 'entity_type', 'slug')

    def __str__(self):
        return str(self.container)

    def get_absolute_url(self):
        return self.container.get_url_for(self)
