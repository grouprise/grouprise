# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-28 09:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0015_auto_20160428_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='file',
            field=models.ImageField(upload_to='', verbose_name='Datei'),
        ),
    ]