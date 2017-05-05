from django import forms

from features.content import forms as content
from . import models


OptionFormSet = forms.modelformset_factory(
        models.Option, extra=3, fields=('title',), labels={'title': 'Antwort'}, max_num=3,
        min_num=1, validate_min=True)


class OptionMixin:
    def is_valid(self):
        return super().is_valid() and self.options.is_valid()

    def save(self, commit=True):
        association = super().save(commit)
        for form in self.options.forms:
            form.instance.poll = association.container
        self.options.save(commit)
        return association


class Create(OptionMixin, content.Create):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = OptionFormSet(
                data=kwargs.get('data'), queryset=models.Option.objects.none())


class Update(OptionMixin, content.Update):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = OptionFormSet(
                data=kwargs.get('data'),
                queryset=models.Option.objects.filter(poll=self.instance.container))
