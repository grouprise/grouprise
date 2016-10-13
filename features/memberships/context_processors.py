from django.db.models import functions


def my_memberships(request):
    return {'my_memberships': request.user.gestalt.memberships.order_by(
        functions.Lower('group__name'))}
