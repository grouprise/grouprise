from django.core.exceptions import ValidationError
from django.core.validators import validate_slug

from grouprise.core.settings import CORE_SETTINGS


def validate_entity_slug(slug, entity=None):
    from grouprise.features.gestalten.models import Gestalt
    from grouprise.features.groups.models import Group

    # validate character set
    validate_slug(slug)

    # validate by blacklist
    if slug.lower() in CORE_SETTINGS.ENTITY_SLUG_BLACKLIST:
        raise ValidationError(
                'Die Adresse \'%(slug)s\' ist reserviert und darf nicht verwendet werden.',
                params={'slug': slug}, code='reserved')

    # validate existing slugs
    gestalten = Gestalt.objects
    groups = Group.objects
    if entity:
        if entity.is_group:
            groups = groups.exclude(pk=entity.pk)
        else:
            gestalten = gestalten.exclude(pk=entity.pk)
    if (groups.filter(slug__iexact=slug).exists()
            or gestalten.filter(user__username__iexact=slug).exists()):
        raise ValidationError(
                'Die Adresse \'%(slug)s\' ist bereits vergeben.',
                params={'slug': slug}, code='in-use')
