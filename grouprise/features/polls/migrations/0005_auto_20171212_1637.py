# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-12 15:37
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content2", "0008_auto_20170620_1022"),
        ("polls", "0004_auto_20170921_1502"),
    ]

    operations = [
        migrations.CreateModel(
            name="CondorcetVote",
            fields=[
                (
                    "vote_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="polls.Vote",
                    ),
                ),
                ("rank", models.SmallIntegerField()),
            ],
            options={
                "abstract": False,
            },
            bases=("polls.vote",),
        ),
        migrations.CreateModel(
            name="Poll",
            fields=[
                (
                    "content_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="content2.Content",
                    ),
                ),
                ("condorcet", models.BooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
            bases=("content2.content",),
        ),
        migrations.CreateModel(
            name="SimpleVote",
            fields=[
                (
                    "vote_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="polls.Vote",
                    ),
                ),
                ("endorse_new", models.NullBooleanField(default=False)),
            ],
            options={
                "abstract": False,
            },
            bases=("polls.vote",),
        ),
        migrations.AddField(
            model_name="option",
            name="poll_new",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="options_new",
                to="polls.Poll",
            ),
        ),
    ]
