from . import models


def events(request):
    return {'events': models.Event.objects.all()}


def statistics(request):
    return {'content_count': models.Content.objects.count}
