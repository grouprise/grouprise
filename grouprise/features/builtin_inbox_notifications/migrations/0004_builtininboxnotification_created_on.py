# Generated by Django 2.2 on 2022-06-21 13:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('builtin_inbox_notifications', '0003_auto_20220615_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='builtininboxnotification',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
