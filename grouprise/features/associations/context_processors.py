from grouprise.features.associations.models import Association


def activity(request):
    num_activity = None
    if request.user.is_authenticated:
        num_activity = Association.objects.active_ordered_user_associations(
            request.user
        ).count()
    return {"num_activity": num_activity}
