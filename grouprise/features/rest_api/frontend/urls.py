from rest_framework.routers import SimpleRouter

from grouprise.features.groups.rest_api import GroupSet
from grouprise.features.polls.rest_api import PollSet
from .views import GestaltSet, GestaltSettingSet, ImageSet, MarkdownView

router = SimpleRouter()

router.register(r'content/markdown', MarkdownView, base_name='markdown')
router.register(r'gestalten', GestaltSet, 'gestalt')
router.register(r'gestalten/(?P<gestalt>\d+)/settings', GestaltSettingSet, 'gestalt_setting')
router.register(r'groups', GroupSet, 'group')
router.register(r'images', ImageSet, 'image')
router.register(r'polls', PollSet, 'polls')
