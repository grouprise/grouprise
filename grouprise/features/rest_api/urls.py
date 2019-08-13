from django.urls import include, path

from .frontend.urls import router as frontend_router
from .transition_connect.urls import router as tc_router


urlpatterns = [
    path('stadt/api/', include(frontend_router.urls)),
    path('stadt/api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('stadt/tc-api/', include(tc_router.urls)),
]
