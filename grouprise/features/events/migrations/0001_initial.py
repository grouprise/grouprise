# Generated by Django 2.1.11 on 2020-01-05 18:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("gestalten", "0014_auto_20190815_0926"),
        ("content2", "0017_content_tags"),
    ]

    operations = [
        migrations.CreateModel(
            name="AttendanceStatement",
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
                    "timestamp",
                    models.DateTimeField(auto_now=True, verbose_name="Last Update"),
                ),
                (
                    "attendee",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gestalten.Gestalt",
                    ),
                ),
                (
                    "content",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="content2.Content",
                    ),
                ),
            ],
        ),
    ]
