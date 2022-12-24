"""
fix the invalid redirect `old_path` values, which were introduced in `0005_normalize_filenames`.

Example:

* wrong: /stadt/media//var/lib/grouprise/media/dz0z360f64e4cch4.PNG
* correct would be: /stadt/media/dz0z360f64e4cch4.PNG

Additionally the target URL was also incorrect:

* wrong: /-/files/42
* correct would be: /-/files/dz0z360f64e4cch4.PNG

See #796
"""

import logging
import re

from django.db import migrations
from django.conf import settings
from django.urls import reverse


logger = logging.getLogger(__name__)


def fix_redirect_sources(apps, schema_editor):
    base_media_url = settings.MEDIA_URL.rstrip("/")
    base_media_directory = settings.MEDIA_ROOT.rstrip("/")
    bad_old_prefix_regex = re.compile(rf"^{base_media_url}/+{base_media_directory}/")
    bad_target_regex = re.compile(r"^/-/(?P<type>files|images)/(?P<pk>\d+)$")
    redirects_model = apps.get_model("redirects", "Redirect")
    redirect_target_models = {
        "files": (apps.get_model("files", "File"), "download-file"),
        "images": (apps.get_model("images", "Image"), "download-image"),
    }
    for redirect in redirects_model.objects.all():
        old_prefix_match = bad_old_prefix_regex.match(redirect.old_path)
        if old_prefix_match:
            fixed_old_path = bad_old_prefix_regex.sub(
                base_media_url + "/", redirect.old_path
            )
            redirect.old_path = fixed_old_path
            redirect.save()
        target_match = bad_target_regex.match(redirect.new_path)
        if target_match:
            target_model, reverse_url_key = redirect_target_models[
                target_match.group("type")
            ]
            try:
                target_obj = target_model.objects.get(pk=target_match.group("pk"))
            except target_model.DoesNotExist:
                logger.warning("Ignoring non-existing item: %s", redirect.new_path)
            else:
                destination_path = reverse(reverse_url_key, args=[target_obj.file.name])
                redirect.new_path = destination_path
                redirect.save()


class Migration(migrations.Migration):

    dependencies = [
        ("files", "0005_normalize_filenames"),
        ("redirects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(fix_redirect_sources),
    ]
