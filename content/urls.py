from . import creation, views
from django.conf import urls

urlpatterns = [
    urls.url(r'^article/$', views.ArticleList.as_view(), name='article-index'),
    urls.url(r'^article/add/$', creation.Article.as_view(), name='article-create'),
    urls.url(r'^(?P<type>article|event|gallery)/add/$', views.ContentCreate.as_view(), name='content-create'),
    urls.url(r'^content/(?P<content_pk>[0-9]+)/comment/add/$', views.CommentCreate.as_view(), name='comment-create'),
    urls.url(r'^content/(?P<pk>[0-9]+)/edit/$', views.ContentUpdate.as_view(), name='content-update'),
    urls.url(r'^event/$', views.EventList.as_view(), name='event-index'),
    urls.url(r'^event/(?P<year>[0-9]{4})/(?P<month>[-\w]+)/(?P<day>[0-9]+)/$', views.EventDay.as_view(), name='event-day'),
    urls.url(r'^gallery/$', views.ContentList.as_view(), name='gallery-index'),
]
