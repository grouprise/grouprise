# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-22 10:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conversations", "0002_auto_20161110_1621"),
    ]

    operations = [
        migrations.AlterField(
            model_name="conversation",
            name="subject",
            field=models.CharField(max_length=255),
        ),
    ]
