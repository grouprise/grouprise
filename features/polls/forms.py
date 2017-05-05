from django import forms

from features.content import forms as content
from . import models


OptionFormSet = forms.modelformset_factory(
        models.Option, extra=3, fields=('title',), labels={'title': 'Antwort'})


class Create(content.Create):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))

    options = OptionFormSet()
