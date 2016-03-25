from . import views
from django.conf import urls

urlpatterns = [
    urls.url(r'^logout/$', views.Logout.as_view(), name='logout'),
]
