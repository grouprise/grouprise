# Generated by Django 2.2 on 2022-06-15 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gestalten', '0016_auto_20210421_1051'),
        ('builtin_inbox_notifications', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='BuiltinNotification',
            new_name='BuiltinInboxNotification',
        ),
    ]
