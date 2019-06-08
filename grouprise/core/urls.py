from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import SimpleRouter

from grouprise.core.rest_api import MarkdownView
from grouprise.core.views import Markdown

# Router for internal REST API providing data for frontend JavaScript functionality.
api_router = SimpleRouter()

api_router.register(r'content/markdown', MarkdownView, base_name='markdown')

urlpatterns = [
    path('stadt/admin/', admin.site.urls),
    path('stadt/markdown/', Markdown.as_view(), name='markdown'),
]


def api():
    return [
        path('stadt/api/', include(api_router.urls)),
        path('stadt/api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    ]