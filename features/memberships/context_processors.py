from django.db.models import functions


def my_memberships(request):
    if request.user.is_authenticated():
        ms = request.user.gestalt.memberships.order_by(functions.Lower('group__name'))
    else:
        ms = []
    return {'my_memberships': ms}
