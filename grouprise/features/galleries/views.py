import grouprise.features.content.views
from . import forms


class Create(grouprise.features.content.views.Create):
    template_name = 'galleries/create.html'

    form_class = forms.Create

    def get_initial(self):
        initial = super().get_initial()
        initial['title'] = self.request.GET.get('title', initial.get('title'))
        initial['text'] = self.request.GET.get('text', initial.get('text'))
        initial['pinned'] = self.request.GET.get('pinned', initial.get('pinned'))
        initial['public'] = self.request.GET.get('public', initial.get('public'))
        return initial
