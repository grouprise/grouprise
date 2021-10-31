from allauth.socialaccount import views as socialaccount_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^stadt/login/$", views.Login.as_view(), name="account_login"),
    url(r"^stadt/logout/$", views.Logout.as_view(), name="account_logout"),
    url(
        r"^stadt/login/cancelled/$",
        socialaccount_views.LoginCancelledView.as_view(
            template_name="auth/login_cancelled.html"
        ),
        name="socialaccount_login_cancelled",
    ),
    url(
        r"^stadt/login/error/$",
        socialaccount_views.login_error,
        name="socialaccount_login_error",
    ),
    url(
        r"^stadt/password/reset/$",
        views.PasswordReset.as_view(),
        name="account_reset_password",
    ),
    url(
        r"^stadt/password/reset/done/$",
        views.PasswordResetDone.as_view(),
        name="account_reset_password_done",
    ),
]
