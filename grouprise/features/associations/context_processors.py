from grouprise.features.associations.models import Association


def activity(request):
    num_activity = None
    if request.user.is_authenticated:
        num_activity = len(Association.objects.active_ordered_user_associations(request.user))
    return {'num_activity': num_activity}
