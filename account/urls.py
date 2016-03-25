from . import views
from allauth.account import views as allauth_views
from django.conf import urls

urlpatterns = [
    urls.url(r'^confirm-email/(?P<key>[-:\w]+)/$', allauth_views.confirm_email, name='account_confirm_email'),
    urls.url(r'^login/$', views.Login.as_view(), name='account_login'),
    urls.url(r'^logout/$', views.Logout.as_view(), name='account_logout'),
    urls.url(r'^signup/$', views.Signup.as_view(), name='account_signup'),
]
