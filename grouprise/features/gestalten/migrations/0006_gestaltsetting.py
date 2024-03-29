# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-07 02:22
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("gestalten", "0005_gestalt_score"),
    ]

    operations = [
        migrations.CreateModel(
            name="GestaltSetting",
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
                ("category", models.CharField(blank=True, max_length=255, null=True)),
                ("name", models.CharField(max_length=255)),
                ("value", models.TextField()),
                (
                    "gestalt",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gestalten.Gestalt",
                    ),
                ),
            ],
        ),
    ]
