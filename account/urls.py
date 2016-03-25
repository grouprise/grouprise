from . import views
from django.conf import urls

urlpatterns = [
    urls.url(r'^login/$', views.Login.as_view(), name='account_login'),
    urls.url(r'^logout/$', views.Logout.as_view(), name='account_logout'),
    urls.url(r'^signup/$', views.Logout.as_view(), name='account_signup'),
]
