from core.urls import api_router
from features.images.rest_api import ImageSet

api_router.register(r'images', ImageSet, 'image')

urlpatterns = []
