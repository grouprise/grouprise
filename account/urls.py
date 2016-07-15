from . import views
from allauth.account import views as allauth_views
from django.conf import urls

urlpatterns = [
    urls.url(r'^confirm/(?P<key>[-:\w]+)/$', views.Confirm.as_view(), name='account_confirm_email'),
    urls.url(r'^email/$', views.Email.as_view(), name='account_email'),
    urls.url(r'^login/$', views.Login.as_view(), name='account_login'),
    urls.url(r'^logout/$', views.Logout.as_view(), name='account_logout'),
    urls.url(r'^password/change/$', views.PasswordChange.as_view(), name='account_change_password'),
    urls.url(r'^password/reset/$', views.PasswordReset.as_view(), name='account_reset_password'),
    urls.url(r'^password/reset/done/$', views.PasswordResetDone.as_view(), name='account_reset_password_done'),
    urls.url(r'^password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$', views.PasswordResetFromKey.as_view(), name='account_reset_password_from_key'),
    urls.url(r'^password/reset/key/done/$', allauth_views.password_reset_from_key_done, name='account_reset_password_from_key_done'),
    urls.url(r'^signup/$', views.Signup.as_view(), name='account_signup'),
]
