from . import views
from django.conf import urls

urlpatterns = [
    urls.url(
        r'^groups/(?P<group_pk>[0-9]+)/members/add/gestalt/'
        r'(?P<gestalt_pk>[0-9]+)/$',
        views.ContentGroupMemberCreate.as_view(),
        name='content-group-member-create'),
]
