# Generated by Django 2.0.2 on 2018-02-06 08:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0019_auto_20180109_1302'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='date_founded',
            field=models.DateField(default=datetime.date.today, help_text='Ungefähres Datum der tatsächlichen Gruppengründung', verbose_name='Gruppe gegründet'),
        ),
    ]
