from django.conf import urls
from . import api

urlpatterns = [
    urls.url(r'^', urls.include(api.router.urls)),
    urls.url(r'^auth/', urls.include('rest_framework.urls', namespace='rest_framework')),
]
