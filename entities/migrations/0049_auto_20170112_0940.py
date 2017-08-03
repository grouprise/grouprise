# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-12 08:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0048_auto_20170112_0931'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gestalt',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='old_user', to=settings.AUTH_USER_MODEL),
        ),
    ]