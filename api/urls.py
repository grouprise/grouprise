from . import views
from django.conf import urls
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'images', views.ImageSet)

urlpatterns = [
    urls.url(r'^', urls.include(router.urls)),
    urls.url(r'^auth/', urls.include('rest_framework.urls', namespace='rest_framework')),
]
