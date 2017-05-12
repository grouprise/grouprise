from django.conf.urls import url

import core.views.markdown

urlpatterns = [
    url(r'^stadt/markdown/$', core.views.markdown.Markdown.as_view(), name='markdown')
]
