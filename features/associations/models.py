"""
Copyright 2016-2017 sense.lab e.V. <info@senselab.org>

This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.contrib.contenttypes import fields as contenttypes
from django.db import models

import core.models
from . import querysets


class Association(core.models.Model):
    pinned = models.BooleanField(
            'Im Intro der Gruppe anheften', default=False,
            help_text='Angeheftete Beiträge werden auf der Gruppenseite zuerst angezeigt. Sie '
            'können beispielsweise für allgemeine Einleitungs- und Beschreibungstexte '
            'verwendet werden.')
    public = models.BooleanField(
            'Öffentlich', default=False,
            help_text='Öffentliche Beiträge sind auch für Besucherinnen sichtbar, die nicht '
            'Mitglied der Gruppe sind')
    slug = models.SlugField(
            'Kurzname', default=None, null=True,
            help_text='Der Kurzname wird beispielsweise in der Webadresse des Beitrags '
            'verwendet.')

    container = contenttypes.GenericForeignKey('container_type', 'container_id')
    container_id = models.PositiveIntegerField()
    container_type = models.ForeignKey(
            'contenttypes.ContentType', related_name='container_associations')

    entity = contenttypes.GenericForeignKey('entity_type', 'entity_id')
    entity_id = models.PositiveIntegerField()
    entity_type = models.ForeignKey(
            'contenttypes.ContentType', related_name='entity_associations')

    objects = models.Manager.from_queryset(querysets.Association)()

    class Meta:
        unique_together = ('entity_id', 'entity_type', 'slug')

    def __str__(self):
        return str(self.container)

    def get_absolute_url(self):
        return self.container.get_url_for(self)
