from allauth.socialaccount import views as socialaccount_views
from allauth.socialaccount.providers.facebook import views as facebook_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/gestalten/$',
        views.List.as_view(),
        name='gestalten'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/$',
        views.Update.as_view(),
        name='gestalt-update'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/avatar/$',
        views.UpdateAvatar.as_view(),
        name='gestalt-avatar-update'),

    url(
        r'^stadt/gestalten/(?P<pk>[0-9]+)/edit/background/$',
        views.UpdateBackground.as_view(),
        name='gestalt-background-update'),

    url(
        r'^stadt/login/$',
        views.Login.as_view(),
        name='login'),

    url(r'^stadt/login/cancelled/$',
        socialaccount_views.login_cancelled,
        name='socialaccount_login_cancelled'),

    url(r'^stadt/login/error/$',
        socialaccount_views.login_error,
        name='socialaccount_login_error'),

    url(r'^stadt/login/signup/$',
        socialaccount_views.signup,
        name='socialaccount_signup'),

    url(r'^stadt/login/facebook/$',
        facebook_views.oauth2_login,
        name='facebook_login'),

    url(r'^stadt/login/facebook/callback/$',
        facebook_views.oauth2_callback,
        name='facebook_callback'),

    url(r'^stadt/login/facebook/token/$',
        facebook_views.login_by_token,
        name='facebook_login_by_token'),
]
