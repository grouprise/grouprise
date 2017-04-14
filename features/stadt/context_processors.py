import django.contrib.auth.hashers

from features.associations import models as associations
from features.gestalten import models as gestalten
from features.groups import models as groups


def page_meta(request):
    return {
            'num_groups': groups.Group.objects.count(),
            'num_gestalten': gestalten.Gestalt.objects.exclude(
                user__password__startswith=django.contrib.auth.hashers.
                UNUSABLE_PASSWORD_PREFIX).count(),
            'num_associations': associations.Association.objects.count(),
            }
