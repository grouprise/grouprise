import django

from features.associations import models as associations
from features.groups import models as groups


class Index(django.contrib.syndication.views.Feed):
    link = django.urls.reverse_lazy('index')
    description_template = 'feeds/detail.html'

    def items(self):
        return associations.Association.objects.ordered_user_content(
                django.contrib.auth.models.AnonymousUser())

    def item_title(self, item):
        return str(item)

    def item_pubdate(self, item):
        return item.container.versions.first().time_created

    def title(self):
        return django.contrib.sites.models.Site.objects.get_current().name


class Group(Index):
    def get_object(self, request, group_pk):
        return django.shortcuts.get_object_or_404(groups.Group, pk=group_pk)

    def items(self, obj):
        return super().items().filter(group=obj)

    def link(self, obj):
        return obj.get_absolute_url()

    def title(self, obj):
        return str(obj)
