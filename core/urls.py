from django.contrib import admin
from django.urls import include, path

from core import api
from core.views import Error
from core.views.markdown import Markdown

urlpatterns = [
    path('stadt/admin/', admin.site.urls),
    path('stadt/api/', include(api.router.urls)),
    path('stadt/api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('stadt/error/', Error.as_view()),
    path('stadt/markdown/', Markdown.as_view(), name='markdown'),
    path('stadt/tc-api/', include(api.tc_router.urls)),
]
