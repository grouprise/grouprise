from rest_framework.routers import SimpleRouter

from .views import EventViewSet, TransitionGroupSet

router = SimpleRouter()

router.register(r"event", EventViewSet, "event")
router.register(r"organisation", TransitionGroupSet, "organisation")
