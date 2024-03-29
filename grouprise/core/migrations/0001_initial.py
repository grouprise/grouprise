# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-19 17:45
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models

import grouprise.core.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("gestalten", "0006_gestaltsetting"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="PermissionToken",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "secret_key",
                    models.CharField(
                        default=grouprise.core.models.generate_token, max_length=15
                    ),
                ),
                ("time_created", models.DateTimeField(auto_now_add=True)),
                ("feature_key", models.CharField(max_length=32)),
                ("target_id", models.PositiveIntegerField()),
                (
                    "gestalt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gestalten.Gestalt",
                    ),
                ),
                (
                    "target_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.ContentType",
                    ),
                ),
            ],
        ),
    ]
