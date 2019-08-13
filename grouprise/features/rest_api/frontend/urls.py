from django.conf.urls import url
from rest_framework.routers import SimpleRouter

from .views import GestaltSet, GestaltSettingSet, GroupSet, ImageSet, MarkdownView, PollSet, vote

router = SimpleRouter()

router.register(r'content/markdown', MarkdownView, base_name='markdown')
router.register(r'gestalten', GestaltSet, 'gestalt')
router.register(r'gestalten/(?P<gestalt>\d+)/settings', GestaltSettingSet, 'gestalt_setting')
router.register(r'groups', GroupSet, 'group')
router.register(r'images', ImageSet, 'image')
router.register(r'polls', PollSet, 'polls')

urlpatterns = [
    url(r'^polls/(?P<pk>[^/.]+)/vote', vote, name='polls-vote'),
]
