from django.urls import include, path
from rest_framework.routers import SimpleRouter

from grouprise.features.groups.rest_api import GroupSet
from grouprise.features.images.rest_api import ImageSet
from grouprise.features.polls.rest_api import PollSet
from grouprise.features.rest_api.frontend.views import GestaltSet, GestaltSettingSet, MarkdownView

api_router = SimpleRouter()

api_router.register(r'content/markdown', MarkdownView, base_name='markdown')
api_router.register(r'gestalten', GestaltSet, 'gestalt')
api_router.register(r'gestalten/(?P<gestalt>\d+)/settings', GestaltSettingSet, 'gestalt_setting')
api_router.register(r'groups', GroupSet, 'group')
api_router.register(r'images', ImageSet, 'image')
api_router.register(r'polls', PollSet, 'polls')


def api():
    return [
        path('stadt/api/', include(api_router.urls)),
        path('stadt/api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]
