from django import forms

from features.content import forms as content
from . import models


OptionFormSet = forms.modelformset_factory(
        models.Option, extra=3, fields=('title',), labels={'title': 'Antwort'}, min_num=1,
        validate_min=True)


class Create(content.Create):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = OptionFormSet(kwargs['data'])

    def is_valid(self):
        return super().is_valid() and self.options.is_valid()

    def save(self, commit=True):
        association = super().save(commit)
        for form in self.options.forms:
            form.instance.poll = association.container
        self.options.save(commit)
        return association
