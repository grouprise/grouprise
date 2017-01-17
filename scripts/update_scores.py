#!/usr/bin/env python
import django
import os
import sys

# Update scores (call in a daily cron job)

PROJECT_ROOT = '/home/robert/stadt'
SETTINGS_MODULE = 'stadt.settings'

if __name__ == '__main__':
    sys.path.append(PROJECT_ROOT)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_MODULE)
    django.setup()

    import core.scores
    import features.gestalten.models
    import features.groups.models
    core.scores.update(features.gestalten.models.Gestalt)
    core.scores.update(features.groups.models.Group)
