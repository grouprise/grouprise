from grouprise.features.content.models import Content
from grouprise.features.contributions.models import Contribution
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group


def page_meta(request):
    return {
        "num_groups": Group.objects.count(),
        "num_gestalten": Gestalt.objects.count(),
        "num_contributions": Contribution.objects.count() + Content.objects.count(),
    }
