from django.urls import path

from grouprise.features.builtin_inbox_notifications.views import ActivityView

urlpatterns = [
    path("stadt/activity", ActivityView.as_view(), name="activity"),
]
