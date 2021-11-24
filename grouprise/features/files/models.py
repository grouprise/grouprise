import io
import os
import tempfile
from typing import List

import django
import django.core.files

from grouprise.core.fields import DownloadFileField
from django.db import models
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFit, Transpose

import grouprise.core
from grouprise.features.contributions import models as contributions
from grouprise.features.imports.mails import ParsedMailAttachment

IGNORE_CONTENT_TYPES = {"application/pgp-signature"}


def get_unique_storage_filename(
    name_template: str, base_dir: str, default_prefix: str = "attachment-"
) -> str:
    """determine a suitable name for a file to be stored in a directory

    The file may not overwrite an existing file and it should keep its original extension.
    """
    temp_kwargs = {"dir": base_dir, "prefix": default_prefix, "delete": False}
    if name_template:
        basename, extension = os.path.splitext(os.path.basename(name_template))
        if extension:
            temp_kwargs["suffix"] = "." + extension
        if basename:
            temp_kwargs["prefix"] = basename + "-"
    storage_file = tempfile.NamedTemporaryFile(**temp_kwargs)
    storage_file.close()
    return storage_file.name


class FileManager(models.Manager):
    def create_from_message_attachments(
        self, attachments: List[ParsedMailAttachment], attached_to
    ):
        for attachment in attachments:
            if attachment.content_type in IGNORE_CONTENT_TYPES:
                continue

            if attachment.data is not None:
                # create the file and reference it
                filename = get_unique_storage_filename(
                    attachment.filename, File.file.field.storage.base_location
                )
                f = self.create()
                f.file.save(
                    os.path.basename(filename),
                    django.core.files.File(io.BytesIO(attachment.data)),
                )
            else:
                file_source = attachment.model_obj
                f = self.create(file=file_source, filename=attachment.filename)
            contributions.Contribution.objects.create(
                container_id=attached_to.container_id,
                container_type=attached_to.container_type,
                contribution_id=f.id,
                contribution_type=f.content_type,
                author=attached_to.author,
                attached_to=attached_to,
            )


class File(grouprise.core.models.Model):
    file = DownloadFileField()
    filename = models.CharField(max_length=255, blank=True, null=True)

    contribution = django.contrib.contenttypes.fields.GenericRelation(
        "contributions.Contribution",
        content_type_field="contribution_type",
        object_id_field="contribution_id",
        related_query_name="file",
    )

    version = models.ForeignKey(
        "content2.Version", null=True, on_delete=models.CASCADE, related_name="file"
    )

    image_480 = ImageSpecField(
        source="file", processors=[Transpose(), ResizeToFit(480)], format="JPEG"
    )
    image_768 = ImageSpecField(
        source="file", processors=[Transpose(), ResizeToFit(768)], format="JPEG"
    )
    image_1200 = ImageSpecField(
        source="file", processors=[Transpose(), ResizeToFit(1200)], format="JPEG"
    )
    image_1920 = ImageSpecField(
        source="file", processors=[Transpose(), ResizeToFit(1920)], format="JPEG"
    )

    objects = FileManager()

    @property
    def display_name(self):
        return self.filename or os.path.basename(self.file.name)

    def __str__(self):
        return self.display_name

    def get_absolute_url(self):
        return self.file.url

    def is_image(self):
        root, ext = os.path.splitext(self.file.name.lower())
        return ext in (".svg", ".apng", ".png", ".gif", ".jpg", ".jpeg")

    def is_video(self):
        root, ext = os.path.splitext(self.file.name.lower())
        return ext in (".mp4", ".ogg", ".webm")

    def is_audio(self):
        root, ext = os.path.splitext(self.file.name.lower())
        return ext in (".opus", ".ogg", ".aac", ".mp3", ".flac", ".m4a")
