from os import path
import re

import django
from django.db import models

import core
from features.contributions import models as contributions


EXCLUDE_RE = r'Content-Type: application/pgp-signature'


class FileManager(models.Manager):
    def create_from_message(self, message, attached_to):
        for attachment in message.attachments.all():
            if re.search(EXCLUDE_RE, attachment.headers):
                continue
            f = self.create(file=attachment.document, filename=attachment.get_filename())
            contributions.Contribution.objects.create(
                    container_id=attached_to.container_id,
                    container_type=attached_to.container_type,
                    contribution_id=f.id,
                    contribution_type=f.content_type,
                    author=attached_to.author,
                    attached_to=attached_to)


class File(core.models.Model):
    file = models.FileField()
    filename = models.CharField(max_length=255, blank=True, null=True)

    contribution = django.contrib.contenttypes.fields.GenericRelation(
            'contributions.Contribution',
            content_type_field='contribution_type',
            object_id_field='contribution_id',
            related_query_name='file')

    version = models.ForeignKey(
            'content2.Version', null=True, on_delete=models.CASCADE, related_name='file')

    objects = FileManager()

    @property
    def display_name(self):
        return self.filename or path.basename(self.file.name)

    def is_image(self):
        root, ext = path.splitext(self.file.name.lower())
        return ext in ('.svg', '.apng', '.png', '.gif', '.jpg', '.jpeg')

    def is_video(self):
        root, ext = path.splitext(self.file.name.lower())
        return ext in ('.mp4', '.ogg', '.webm')

    def is_audio(self):
        root, ext = path.splitext(self.file.name.lower())
        return ext in ('.opus', '.ogg', '.aac', '.mp3', '.flac', '.m4a')
