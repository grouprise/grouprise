from core import signals
from django.contrib import auth
from django.core import cache
from django.core.cache import utils
from entities import models as gestalten
from features.groups import models as groups


def invalidate_cache(fragment, *args):
    cache.cache.delete(utils.make_template_fragment_key(fragment, args))


def gestalt_changed(gestalt_or_user):
    try:
        user = gestalt_or_user.user
    except AttributeError:
        user = gestalt_or_user
    invalidate_cache('site-menu', user.username, None)
    for group in groups.Group.objects.all():
        invalidate_cache('site-menu', user.username, group.slug)


connections = [
    signals.connect_action(
        signals.model_changed,
        gestalt_changed,
        senders=[gestalten.Gestalt, auth.get_user_model()])
    ]
