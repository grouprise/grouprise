from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/groups/$',
        views.List.as_view(),
        name='group-index'),

    url(
        r'^stadt/groups/add/$',
        views.Create.as_view(),
        name='group-create'),

    url(
        r'^stadt/settings/group/$',
        views.Update.as_view(),
        name='group-settings'),

    url(
        r'^stadt/settings/group/images/$',
        views.ImageUpdate.as_view(),
        name='group-image-settings'),

    url(
        r'^stadt/settings/group/subscriptions-memberships/$',
        views.SubscriptionsMemberships.as_view(),
        name='subscriptions-memberships-settings'),
]
