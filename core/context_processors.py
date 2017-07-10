import django


def settings(request):
    return {
            'STADTGESTALTEN_LOGO_URL': django.conf.settings.STADTGESTALTEN_LOGO_URL,
            'STADTGESTALTEN_SHORT_NAME': django.conf.settings.STADTGESTALTEN_SHORT_NAME,
            'STADTGESTALTEN_SHOW_HEADER': django.conf.settings.STADTGESTALTEN_SHOW_HEADER,
            }
