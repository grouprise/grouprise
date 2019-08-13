from allauth.account import views as allauth_views
from allauth.socialaccount import views as socialaccount_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/signup/$',
        views.Create.as_view(),
        name='account_signup'),

    url(r'^stadt/login/signup/$',
        socialaccount_views.signup,
        name='socialaccount_signup'),

    url(
        r'^stadt/gestalten/$',
        views.List.as_view(),
        name='gestalten'),

    url(
        r'^stadt/settings/$',
        views.Update.as_view(),
        name='settings'),

    url(
        r'^stadt/settings/gestalt/delete/$',
        views.Delete.as_view(),
        name='delete-gestalt'),

    url(
        r'^stadt/settings/images/$',
        views.UpdateImages.as_view(),
        name='image-settings'),

    url(r'^stadt/email/$',
        views.UpdateEmail.as_view(),
        name='email-settings'),

    url(
        r'^stadt/confirm/(?P<key>[-:\w]+)/$',
        views.UpdateEmailConfirm.as_view(),
        name='account_confirm_email'),

    url(
        r'^stadt/settings/password/$',
        views.UpdatePassword.as_view(),
        name='account_change_password'),

    url(
        r'^stadt/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$',
        views.UpdatePasswordKey.as_view(),
        name='account_reset_password_from_key'),

    url(
        r'^stadt/password/reset/key/done/$',
        allauth_views.password_reset_from_key_done,
        name='account_reset_password_from_key_done'),

    url(
        r'^stadt/password/set/$',
        views.UpdatePasswordSet.as_view(),
        name='account_set_password'),
]
