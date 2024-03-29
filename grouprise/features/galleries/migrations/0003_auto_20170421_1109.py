# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-21 09:09
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("galleries", "0002_auto_20170421_0934"),
    ]

    operations = [
        migrations.AlterField(
            model_name="galleryimage",
            name="gallery",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="gallery_images",
                to="content2.Content",
            ),
        ),
    ]
