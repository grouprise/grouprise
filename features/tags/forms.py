from django import forms
from django.db.models.functions import Lower

from . import models


class TagGroup(forms.ModelForm):
    class Meta:
        model = models.Tagged
        fields = []

    group = forms.ModelChoiceField(label='Gruppe', queryset=None)

    def __init__(self, **kwargs):
        tagger = kwargs.pop('tagger')
        super().__init__(**kwargs)
        self.fields['group'].queryset = tagger.groups.exclude(
                tags__tag=self.instance.tag).order_by(Lower('name'))

    def save(self, commit=True):
        if commit and not self.instance.tag.pk:
            self.instance.tag.save()
            self.instance.tag_id = self.instance.tag.id
        self.instance.tagged = self.cleaned_data['group']
        return super().save(commit)
