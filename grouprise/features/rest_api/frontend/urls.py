from rest_framework.routers import SimpleRouter

from .views import (
    GestaltSet,
    GestaltSettingSet,
    GroupSet,
    ImageSet,
    MarkdownView,
    PollSet,
)

router = SimpleRouter()

router.register(r"content/markdown", MarkdownView, basename="markdown")
router.register(r"gestalten", GestaltSet, "gestalt")
router.register(
    r"gestalten/(?P<gestalt>\d+)/settings", GestaltSettingSet, "gestalt_setting"
)
router.register(r"groups", GroupSet, "group")
router.register(r"images", ImageSet, "image")
router.register(r"polls", PollSet, "polls")
