import mmap
import re

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand, CommandError

from grouprise.features.content.models import Version
from grouprise.features.contributions.models import Contribution


class Command(BaseCommand):
    TAGS_PATTERN = rb"COPY public\.tags_tag.*?;\s*(.*?)\\\."
    LINKS_PATTERN = rb"COPY public\.tags_tagged.*?;\s*(.*?)\\\."

    help = "Restores tags from a grouprise 2.x database dump."

    def add_arguments(self, parser):
        parser.add_argument(
            "dump_file", help="filename of version 2.x SQL database dump"
        )

    def handle(self, *args, **options):
        def get_data(pattern_str):
            pattern = re.compile(pattern_str, re.DOTALL | re.MULTILINE)
            tag_match = pattern.search(mm)
            if tag_match:
                for dataset in tag_match[1].splitlines():
                    yield dataset.decode().split(sep="\t")
            else:
                raise CommandError("Dump file does not contain tag data")

        dump_file = options.get("dump_file")

        with open(dump_file, "r") as f:
            with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
                tags = {
                    int(data[0]): {"name": data[1], "slug": data[2]}
                    for data in get_data(self.TAGS_PATTERN)
                }
                links = [
                    {
                        "tagged": int(data[1]),
                        "tagged_type": int(data[2]),
                        "tag": int(data[3]),
                    }
                    for data in get_data(self.LINKS_PATTERN)
                ]

        for link in links:
            content_type = ContentType.objects.get_for_id(link["tagged_type"])
            try:
                model = content_type.get_object_for_this_type(id=link["tagged"])
            except ObjectDoesNotExist:
                self.stderr.write(
                    "Warning: Tagged object does no longer exist (type {}, id {})".format(
                        link["tagged_type"], link["tagged"]
                    )
                )
                continue
            if isinstance(model, Contribution):
                model = model.container
            elif isinstance(model, Version):
                model = model.content

            if hasattr(model, "tags"):
                tag_name = tags[link["tag"]]["name"]
                if len(tag_name) <= 100:
                    model.tags.add(tag_name)
                else:
                    self.stderr.write(
                        "Warning: Tag name is too long: {}".format(tag_name)
                    )
            else:
                self.stderr.write(
                    "Warning: Model of type {} is not taggable".format(
                        model.__class__.__name__
                    )
                )
