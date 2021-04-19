# Generated by Django 2.2.13 on 2021-04-19 07:47

from django.db import migrations
import grouprise.features.stadt.models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0025_auto_20210419_0938'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='slug',
            field=grouprise.features.stadt.models.EntitySlugField(help_text='Wird auch als Kurzname verwendet', unique=True, verbose_name='Adresse der Gruppenseite'),
        ),
    ]
