# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-22 08:59
from __future__ import unicode_literals

import django
import django.db.models.deletion
from django.db import migrations, models

import grouprise.core
import grouprise.core.models
import grouprise.core.utils


def no_validator(arg):
    pass


def validate_reservation(value):
    if value in ["gestalt", "stadt"]:
        raise exceptions.ValidationError(
            "Die Adresse '%(value)s' darf nicht verwendet werden.",
            params={"value": value},
            code="reserved",
        )


class AutoSlugField(django.db.models.SlugField):
    def __init__(self, *args, **kwargs):
        self.dodging = True
        if "dodging" in kwargs:
            self.dodging = kwargs.pop("dodging")
        self.populate_from = kwargs.pop("populate_from")
        self.reserve = []
        if "reserve" in kwargs:
            self.reserve = kwargs.pop("reserve")
        kwargs["validators"] = [validate_reservation]
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["populate_from"] = self.populate_from
        kwargs["reserve"] = self.reserve
        return name, path, args, kwargs

    def pre_save(self, model_instance, add):
        if add:
            value = self.slugify(
                type(model_instance),
                self.attname,
                getattr(model_instance, self.populate_from),
                validate_reservation,
                self.dodging,
            )[:45]
            setattr(model_instance, self.attname, value)
            return value
        else:
            return super().pre_save(model_instance, add)

    def slugify(self, model, field, value, validator=no_validator, dodging=True):
        orig_slug = slug = grouprise.core.text.slugify(value)
        if not dodging:
            return slug
        i = 0
        while True:
            try:
                try:
                    validator(slug)
                except exceptions.ValidationError:
                    pass
                else:
                    model.objects.get(**{field: slug})
                i += 1
                slug = orig_slug + "-" + str(i)
            except model.DoesNotExist:
                return slug


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("gestalten", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("date_created", models.DateField(auto_now_add=True)),
                ("name", models.CharField(max_length=255, verbose_name="Name")),
                (
                    "slug",
                    AutoSlugField(
                        populate_from="name",
                        reserve=["gestalt", "stadt"],
                        unique=True,
                        validators=[validate_reservation],
                        verbose_name="Adresse der Gruppenseite",
                    ),
                ),
                ("address", models.TextField(blank=True, verbose_name="Anschrift")),
                ("avatar", models.ImageField(blank=True, upload_to="")),
                (
                    "avatar_color",
                    models.CharField(
                        default=grouprise.core.utils.get_random_color, max_length=7
                    ),
                ),
                (
                    "date_founded",
                    models.DateField(
                        blank=True, null=True, verbose_name="Gruppe gegründet"
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        default="",
                        max_length=200,
                        verbose_name="Kurzbeschreibung",
                    ),
                ),
                ("logo", models.ImageField(blank=True, upload_to="")),
                ("url", models.URLField(blank=True, verbose_name="Adresse im Web")),
                (
                    "closed",
                    models.BooleanField(
                        default=False,
                        help_text="Nur Mitglieder können neue Mitglieder aufnehmen.",
                        verbose_name="Geschlossene Gruppe",
                    ),
                ),
                (
                    "gestalt_created",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="gestalten.Gestalt",
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
        ),
    ]
