from allauth.account import views as allauth_views
from allauth.socialaccount import views as socialaccount_views
from django.urls import path, re_path

from . import views
from .views import NotificationSettingsUpdateView

urlpatterns = [
    re_path(r"^stadt/signup/$", views.Create.as_view(), name="account_signup"),
    re_path(
        r"^stadt/login/signup/$",
        socialaccount_views.signup,
        name="socialaccount_signup",
    ),
    re_path(r"^stadt/gestalten/$", views.List.as_view(), name="gestalten"),
    re_path(r"^stadt/settings/$", views.Update.as_view(), name="settings"),
    re_path(
        r"^stadt/settings/gestalt/delete/$",
        views.Delete.as_view(),
        name="delete-gestalt",
    ),
    re_path(
        r"^stadt/settings/images/$", views.UpdateImages.as_view(), name="image-settings"
    ),
    path(
        "stadt/settings/notifications/",
        NotificationSettingsUpdateView.as_view(),
        name="notification-settings",
    ),
    re_path(r"^stadt/email/$", views.UpdateEmail.as_view(), name="email-settings"),
    re_path(
        r"^stadt/confirm/(?P<key>[-:\w]+)/$",
        views.UpdateEmailConfirm.as_view(),
        name="account_confirm_email",
    ),
    re_path(
        r"^stadt/settings/password/$",
        views.UpdatePassword.as_view(),
        name="account_change_password",
    ),
    re_path(
        r"^stadt/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        views.UpdatePasswordKey.as_view(),
        name="account_reset_password_from_key",
    ),
    re_path(
        r"^stadt/password/reset/key/done/$",
        allauth_views.password_reset_from_key_done,
        name="account_reset_password_from_key_done",
    ),
    re_path(
        r"^stadt/password/set/$",
        views.UpdatePasswordSet.as_view(),
        name="account_set_password",
    ),
]
