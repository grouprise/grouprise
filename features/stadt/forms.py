from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_slug

DEFAULT_ENTITY_SLUG_BLACKLIST = [
        'all', 'grouprise', 'info', 'mail', 'noreply', 'postmaster', 'reply', 'stadt',
        'webmaster', 'www']

ENTITY_SLUG_BLACKLIST = settings.GROUPRISE.get(
        'ENTITY_SLUG_BLACKLIST', DEFAULT_ENTITY_SLUG_BLACKLIST)


def validate_entity_slug(slug, entity=None):
    from features.gestalten.models import Gestalt
    from features.groups.models import Group

    # validate character set
    validate_slug(slug)

    # validate by blacklist
    if slug.lower() in ENTITY_SLUG_BLACKLIST:
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
