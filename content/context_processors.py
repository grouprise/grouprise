from . import models


def stats(request):
    return {'content_count': models.Content.objects.count}
