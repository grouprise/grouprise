
    urls.url(r'^group/attention/(?P<pk>[0-9]+)/delete/$', views.GroupAttentionDelete.as_view(), name='group-attention-delete'),
    urls.url(r'^group/(?P<group_pk>[0-9]+)/pay_attention/$', views.GroupAttentionCreate.as_view(), name='group-attention-create'),
    urls.url(r'^content/(?P<content_pk>[0-9]+)/attention/pay/$', entities_views.AttentionCreate.as_view(), name='attention-create'),
    urls.url(r'^content/(?P<content_pk>[0-9]+)/attention/unpay/$', entities_views.AttentionDelete.as_view(), name='attention-delete'),
