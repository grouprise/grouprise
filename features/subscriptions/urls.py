from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^content/(?P<content_pk>[0-9]+)/subscribe/$',
        views.ContentSubscribe.as_view(),
        name='content-subscribe'),

    urls.url(
        r'^content/(?P<content_pk>[0-9]+)/unsubscribe/$',
        views.ContentUnsubscribe.as_view(),
        name='content-unsubscribe'),

    #urls.url(r'^group/attention/(?P<pk>[0-9]+)/delete/$', views.GroupAttentionDelete.as_view(), name='group-attention-delete'),
    #urls.url(r'^group/(?P<group_pk>[0-9]+)/pay_attention/$', views.GroupAttentionCreate.as_view(), name='group-attention-create'),
]
