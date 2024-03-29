# Generated by Django 2.2 on 2022-06-15 17:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contributions', '0013_auto_20190408_0027'),
        ('content2', '0017_content_tags'),
        ('builtin_inbox_notifications', '0002_auto_20220615_1928'),
    ]

    operations = [
        migrations.AddField(
            model_name='builtininboxnotification',
            name='created_content',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='content2.Content'),
        ),
        migrations.AddField(
            model_name='builtininboxnotification',
            name='created_contribution',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to='contributions.Contribution'),
        ),
    ]
