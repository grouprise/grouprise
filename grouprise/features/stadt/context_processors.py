from features.content.models import Content
from features.contributions.models import Contribution
from features.gestalten.models import Gestalt
from features.groups.models import Group


def page_meta(request):
    return {
            'num_groups': Group.objects.count(),
            'num_gestalten': Gestalt.objects.count(),
            'num_contributions': Contribution.objects.count() + Content.objects.count(),
            }
