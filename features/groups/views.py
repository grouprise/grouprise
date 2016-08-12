from content import models as content_models
from entities import models as entities_models


class GroupMixin:
    def get_context_data(self, **kwargs):
        kwargs['group'] = self.get_group()
        return super().get_context_data(**kwargs)

    def get_group(self):
        for attr in ('object', 'related_object'):
            if hasattr(self, attr):
                instance = getattr(self, attr)
                if isinstance(instance, entities_models.Group):
                    return instance
                if hasattr(instance, 'group'):
                    return instance.group
                if hasattr(instance, 'groups'):
                    return instance.groups.first()
        try:
            if 'group_pk' in self.kwargs:
                return entities_models.Group.objects.get(
                        pk=self.kwargs['group_pk'])
            if 'group_slug' in self.kwargs:
                return entities_models.Group.objects.get(
                        slug=self.kwargs['group_slug'])
            if 'group' in self.request.GET:
                return entities_models.Group.objects.get(
                        slug=self.request.GET['group'])
            if 'content_pk' in self.kwargs:
                return content_models.Content.objects.get(
                        pk=self.kwargs['content_pk']).groups.first()
        except (content_models.Content.DoesNotExist,
                entities_models.Group.DoesNotExist):
            pass
        return None
