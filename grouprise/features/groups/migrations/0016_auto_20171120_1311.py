# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-20 12:11
from __future__ import unicode_literals

from django.db import migrations, models

import grouprise.core.models


class Migration(migrations.Migration):

    dependencies = [
        ("groups", "0015_auto_20171117_1723"),
    ]

    operations = [
        migrations.AlterField(
            model_name="group",
            name="avatar",
            field=grouprise.core.models.ImageField(
                blank=True,
                help_text="Der Avatar ist ein kleines quadratisches Vorschaubild, an welchem sich die Gruppe leicht erkennen lässt.",
                upload_to="",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="closed",
            field=models.BooleanField(
                default=False,
                help_text="In eine geschlossene Gruppe können nur Mitglieder neue Mitglieder aufnehmen.",
                verbose_name="Geschlossene Gruppe",
            ),
        ),
        migrations.AlterField(
            model_name="group",
            name="logo",
            field=grouprise.core.models.ImageField(
                blank=True,
                help_text="Das Logo wird auf der Gruppenseite rechts angezeigt.",
                upload_to="",
            ),
        ),
    ]
