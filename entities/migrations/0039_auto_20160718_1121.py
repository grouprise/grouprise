# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-18 09:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entities', '0038_auto_20160718_1045'),
        ('memberships', '0002_auto_20160718_1052'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='membership',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='membership',
            name='gestalt',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='group',
        ),
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(related_name='groups', through='memberships.Membership', to='entities.Gestalt'),
        ),
        migrations.DeleteModel(
            name='Membership',
        ),
    ]
