# Generated by Django 2.1.3 on 2018-11-08 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0011_auto_20180529_1026'),
    ]

    operations = [
        migrations.AddField(
            model_name='contribution',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]