from . import models


def statistics(request):
    return {'content_count': models.Content.objects.count}
