# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 09:00
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("groups", "0004_auto_20161027_1028"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="gestalt_created",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="gestalten.Gestalt",
            ),
        ),
    ]
