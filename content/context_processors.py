from . import models


def events(request):
    e = models.Event.objects.all()
    dates = map(lambda t: t.date(), e.values_list('time', flat=True))
    return {'events': dict(zip(dates, e))}


def statistics(request):
    return {'content_count': models.Content.objects.count}
