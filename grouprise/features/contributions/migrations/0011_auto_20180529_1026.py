# Generated by Django 2.0.5 on 2018-05-29 08:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("contributions", "0010_auto_20180123_1057"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contribution",
            name="attached_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="attachments",
                to="contributions.Contribution",
            ),
        ),
    ]
