from django.contrib.sites import shortcuts


def site(request):
    return {'site': shortcuts.get_current_site(request)}
