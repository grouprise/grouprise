from django.conf.urls import url

from features.content import views as content

urlpatterns = [
    url(
        r'^$',
        content.List.as_view(template_name='stadt/index.html'),
        name='index',
    ),
]
