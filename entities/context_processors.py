from . import models


def stats(request):
    return {'gestalt_count': models.Gestalt.objects.count, 'group_count': models.Group.objects.count}
