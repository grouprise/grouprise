from django.urls import include, path
from rest_framework.routers import SimpleRouter

from grouprise.features.events.rest_api import EventViewSet
from grouprise.features.groups.rest_api import TransitionGroupSet

# Router for Transition Connect interface.
# http://www.transition-connect.org/
router = SimpleRouter()

router.register(r'event', EventViewSet, 'event')
router.register(r'organisation', TransitionGroupSet, 'organisation')
