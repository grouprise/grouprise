from allauth.socialaccount import views as socialaccount_views
from allauth.socialaccount.providers.facebook import views as facebook_views
from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        r'^stadt/login/$',
        views.Login.as_view(),
        name='login'),

    url(r'^stadt/logout/$', views.Logout.as_view(), name='account_logout'),

    url(r'^stadt/login/cancelled/$',
        socialaccount_views.LoginCancelledView.as_view(
            template_name='auth/login_cancelled.html'),
        name='socialaccount_login_cancelled'),

    url(r'^stadt/login/error/$',
        socialaccount_views.login_error,
        name='socialaccount_login_error'),

    url(r'^stadt/login/facebook/$',
        facebook_views.oauth2_login,
        name='facebook_login'),

    url(r'^stadt/login/facebook/callback/$',
        facebook_views.oauth2_callback,
        name='facebook_callback'),

    url(r'^stadt/login/facebook/token/$',
        facebook_views.login_by_token,
        name='facebook_login_by_token'),

    url(
        r'^stadt/password/reset/$',
        views.PasswordReset.as_view(),
        name='account_reset_password'),

    url(
        r'^stadt/password/reset/done/$',
        views.PasswordResetDone.as_view(),
        name='account_reset_password_done'),
]
