# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-27 07:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_auto_20160922_1108'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
