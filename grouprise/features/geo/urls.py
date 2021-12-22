from django.conf.urls import url

from .settings import GEO_SETTINGS

urlpatterns = []

if GEO_SETTINGS.ENABLED:
    from . import views

    urlpatterns += [
        url(
            r"^stadt/settings/group/geo/$",
            views.UpdateGroupLocationSettings.as_view(),
            name="geo-settings-group",
        ),
    ]
