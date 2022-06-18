from allauth.socialaccount import views as socialaccount_views
from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r"^stadt/login/$", views.Login.as_view(), name="account_login"),
    re_path(r"^stadt/logout/$", views.Logout.as_view(), name="account_logout"),
    re_path(
        r"^stadt/login/cancelled/$",
        socialaccount_views.LoginCancelledView.as_view(
            template_name="auth/login_cancelled.html"
        ),
        name="socialaccount_login_cancelled",
    ),
    re_path(
        r"^stadt/login/error/$",
        socialaccount_views.login_error,
        name="socialaccount_login_error",
    ),
    re_path(
        r"^stadt/password/reset/$",
        views.PasswordReset.as_view(),
        name="account_reset_password",
    ),
    re_path(
        r"^stadt/password/reset/done/$",
        views.PasswordResetDone.as_view(),
        name="account_reset_password_done",
    ),
]
