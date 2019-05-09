from django.contrib.auth.models import AnonymousUser
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy

from grouprise.features.associations.models import Association
from grouprise.features.groups.models import Group


class IndexFeed(Feed):
    link = reverse_lazy('index')
    description_template = 'feeds/detail.html'

    def items(self):
        return Association.objects.ordered_user_content(AnonymousUser()).filter_articles()[:10]

    def item_title(self, item):
        return str(item)

    def item_pubdate(self, item):
        return item.container.versions.first().time_created

    def title(self):
        return Site.objects.get_current().name


class GroupFeed(IndexFeed):
    def get_object(self, request, group_pk):
        return get_object_or_404(Group, pk=group_pk)

    def items(self, obj):
        return Association.objects.filter(group=obj).ordered_user_content(AnonymousUser()) \
                .filter_articles()[:10]

    def link(self, obj):
        return obj.get_absolute_url()

    def title(self, obj):
        return str(obj)
