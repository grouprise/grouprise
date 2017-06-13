import itertools

import django.contrib.contenttypes.models
from django.contrib.contenttypes import models as contenttypes_models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core import exceptions
from django.db import models
from django.utils import crypto

from core import text


PERMISSION_TOKEN_LENGTH = 15


def get_unique_slug(cls, fields, reserved_slugs=[], reserved_slug_qs=None,
        reserved_slug_qs_field='slug'):
    def replace(d, key, repl):
        result = d.copy()
        result[key] = repl
        return result

    slug_field_name = 'slug'
    l = cls._meta.get_field(slug_field_name).max_length
    for i in itertools.count():
        slug = fields[slug_field_name][:l]
        if i:
            suffix = '-{}'.format(i)
            if len(slug) + len(suffix) <= l:
                slug = slug + suffix
            else:
                slug = slug[:-(len(slug)+len(suffix)-l)] + suffix
        if (slug not in reserved_slugs 
                and (reserved_slug_qs is None
                    or not reserved_slug_qs.filter(**{reserved_slug_qs_field: slug}).exists())
                and not cls._default_manager.filter(
                    **replace(fields, slug_field_name, slug)).exists()):
            return slug


class Model(models.Model):
    class Meta:
        abstract = True

    class ContentType:
        def __get__(self, instance, owner):
            return django.contrib.contenttypes.models.ContentType.objects.get_for_model(owner)

    content_type = ContentType()


def generate_token():
    return crypto.get_random_string(length=PERMISSION_TOKEN_LENGTH,
                                    allowed_chars='abcdefghijklmnopqrstuvwxyz0123456789')


class PermissionToken(models.Model):
    """ permission token are bound to a user and a specific resource

    Permission tokens are used for accessing resources like non-public calendars without exposing
    an account password.
    Permission tokens are application/feature-specific. Every application/feature needs to define
    its own unique string (see 'feature_key' below).
    Every permission tokens connects a specific user identity (gestalt) to a specific database
    entity for a specific purpose.

    A permission token may only be used for authentication - never for authorization.
    After retrieving a permission token for a specific purpose, you need to verify that the
    authenticated user is really allowed to access the given resource.
    """
    gestalt = models.ForeignKey('gestalten.Gestalt')
    # FIXME: secret_key should be unique
    secret_key = models.CharField(max_length=PERMISSION_TOKEN_LENGTH, default=generate_token)
    time_created = models.DateTimeField(auto_now_add=True)
    # Every feature (e.g. the calendar) defines its own unique string describing its permission
    # token (e.g. "calendar-read").
    feature_key = models.CharField(max_length=32)
    target_type = models.ForeignKey(contenttypes_models.ContentType)
    target_id = models.PositiveIntegerField()
    target = GenericForeignKey('target_type', 'target_id')

    @classmethod
    def get_permission_token(cls, gestalt, target, feature_key, create_if_missing=False):
        target_object_type = contenttypes_models.ContentType.objects.get_for_model(target)
        token = PermissionToken.objects.filter(gestalt=gestalt, feature_key=feature_key,
                                               target_type=target_object_type.id,
                                               target_id=target.id).first()
        if token:
            return token
        elif create_if_missing:
            new_obj = PermissionToken(gestalt=gestalt, target=target, feature_key=feature_key)
            new_obj.save()
            return new_obj
        else:
            return None

    @classmethod
    def remove_permission_token(cls, gestalt, target, feature_key):
        token = cls.get_permission_token(gestalt, target, feature_key)
        if token:
            token.delete()
