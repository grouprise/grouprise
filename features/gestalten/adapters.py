import allauth
import django

import core
from features.groups import models as groups
from features.stadt.forms import ENTITY_SLUG_BLACKLIST


class AccountAdapter(allauth.account.adapter.DefaultAccountAdapter):
    def generate_unique_username(self, txts, regex=None):
        username = super().generate_unique_username(txts, regex)
        username = core.models.get_unique_slug(
                django.contrib.auth.get_user_model(), {'username': username},
                reserved_slugs=ENTITY_SLUG_BLACKLIST,
                reserved_slug_qs=groups.Group.objects, slug_field_name='username')
        return username
