#!/usr/bin/env python
import django
import os
import sys

# Mass subscribe emails in FILENAME to group with GROUP_SLUG

PROJECT_ROOT = '/home/test/stadt'
SETTINGS_MODULE = 'stadt.settings'
FILENAME = '/home/test/test.txt'
GROUP_SLUG = 'wohnprojekte'

if __name__ == '__main__':
    sys.path.append(PROJECT_ROOT)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()

    emails = []
    with open(FILENAME) as f:
        emails = f.readlines()

    for email in [e.strip() for e in emails]:
        from django.db.utils import IntegrityError
        from entities.models import Gestalt, Group
        from features.subscriptions.models import Subscription
        gestalt = Gestalt.get_or_create(email)
        group = Group.objects.get(slug=GROUP_SLUG)
        try:
            Subscription.objects.create(
                    subscribed_to=group, subscriber=gestalt)
        except IntegrityError:
            pass
