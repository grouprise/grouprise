from django.contrib.sites import shortcuts


def site(request):
    return {'current_site': shortcuts.get_current_site(request)}
