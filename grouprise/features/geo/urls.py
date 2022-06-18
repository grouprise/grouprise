from django.urls import re_path

from .settings import GEO_SETTINGS

urlpatterns = []

if GEO_SETTINGS.ENABLED:
    from . import views

    urlpatterns += [
        re_path(
            r"^stadt/settings/group/geo/$",
            views.UpdateGroupLocationSettings.as_view(),
            name="geo-settings-group",
        ),
    ]
