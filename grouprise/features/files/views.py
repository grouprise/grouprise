import grouprise.features.content.views
from . import forms


class Create(grouprise.features.content.views.Create):
    template_name = 'files/create.html'

    form_class = forms.Create
