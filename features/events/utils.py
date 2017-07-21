from django.utils import timezone


def get_requested_time(request):
    query = request.GET
    month, year = query.get('month', None), query.get('year', None)

    if month and year:
        return timezone.datetime(year=int(year), month=int(month), day=1)
    else:
        return None
