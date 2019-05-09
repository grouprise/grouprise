import features
from . import forms


class Create(features.content.views.Create):
    template_name = 'files/create.html'

    form_class = forms.Create
