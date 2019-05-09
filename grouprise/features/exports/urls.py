from django.urls import include, path
from rest_framework.routers import SimpleRouter

from grouprise.features.events.rest_api import EventViewSet
from grouprise.features.groups.rest_api import TransitionGroupSet

# Router for Transition Connect interface.
# http://www.transition-connect.org/
tc_router = SimpleRouter()

tc_router.register(r'event', EventViewSet, 'event')
tc_router.register(r'organisation', TransitionGroupSet, 'organisation')

urlpatterns = [
    path('stadt/tc-api/', include(tc_router.urls)),
]
