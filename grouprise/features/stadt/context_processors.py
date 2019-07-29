from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.contributions.models import Contribution
from grouprise.features.gestalten.models import Gestalt
from grouprise.features.groups.models import Group


def page_meta(request):
    num_activity = None
    if request.user.is_authenticated:
        num_activity = Association.objects.ordered_user_conversations(request.user) \
                .filter(last_activity__gte=request.user.gestalt.activity_bookmark_time) \
                .count()
    return {
            'num_groups': Group.objects.count(),
            'num_gestalten': Gestalt.objects.count(),
            'num_contributions': Contribution.objects.count() + Content.objects.count(),
            'num_activity': num_activity,
            }
