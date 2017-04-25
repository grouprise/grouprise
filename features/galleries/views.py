import features.content.views
from . import forms


class Create(features.content.views.Create):
    template_name = 'galleries/create.html'

    form_class = forms.Create
