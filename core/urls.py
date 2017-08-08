from django.conf.urls import url

import core.views.markdown

urlpatterns = [
    url(r'^stadt/error/$', core.views.Error.as_view()),
    url(r'^stadt/markdown/$', core.views.markdown.Markdown.as_view(), name='markdown'),
]
