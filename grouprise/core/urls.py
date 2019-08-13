from django.contrib import admin
from django.urls import path

from grouprise.core.views import Markdown


urlpatterns = [
    path('stadt/admin/', admin.site.urls),
    path('stadt/markdown/', Markdown.as_view(), name='markdown'),
]
