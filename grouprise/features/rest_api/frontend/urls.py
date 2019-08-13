from django.urls import include, path
from rest_framework.routers import SimpleRouter

from grouprise.features.rest_api.frontend.views import GestaltSet, GestaltSettingSet, MarkdownView

api_router = SimpleRouter()

api_router.register(r'content/markdown', MarkdownView, base_name='markdown')
api_router.register(r'gestalten', GestaltSet, 'gestalt')
api_router.register(r'gestalten/(?P<gestalt>\d+)/settings', GestaltSettingSet, 'gestalt_setting')


def api():
    return [
        path('stadt/api/', include(api_router.urls)),
        path('stadt/api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]
