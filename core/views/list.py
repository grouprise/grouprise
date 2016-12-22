from . import base
from django.views.generic import list as django


class BaseListView(django.MultipleObjectMixin, base.View):
    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        return self.render_to_response(self.get_context_data())


class ListView(django.MultipleObjectTemplateResponseMixin, BaseListView):
    pass
