# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-16 08:34
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("content2", "0006_auto_20170421_0909"),
        ("gestalten", "0007_remove_gestalt_addressed_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="Option",
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
                ("title", models.CharField(max_length=255)),
                (
                    "poll",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="content2.Content",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Vote",
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
                ("anonymous", models.CharField(blank=True, max_length=63, null=True)),
                ("time_updated", models.DateTimeField(auto_now=True)),
                ("endorse", models.BooleanField(default=False)),
                (
                    "option",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="polls.Option"
                    ),
                ),
                (
                    "voter",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="votes",
                        to="gestalten.Gestalt",
                    ),
                ),
            ],
        ),
        migrations.AlterUniqueTogether(
            name="vote",
            unique_together=set([("option", "voter"), ("option", "anonymous")]),
        ),
    ]
