# Generated by Django 2.2.25 on 2021-12-13 11:29

from django.db import migrations
import grouprise.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0003_auto_20180109_1302"),
    ]

    operations = [
        migrations.AlterField(
            model_name="image",
            name="file",
            field=grouprise.core.fields.DownloadImageField(
                upload_to="", verbose_name="Datei"
            ),
        ),
    ]
