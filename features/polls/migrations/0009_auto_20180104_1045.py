# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-04 09:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0008_auto_20180104_1045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='poll',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='options', to='polls.Poll'),
        ),
    ]