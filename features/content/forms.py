from django import forms

import core.forms
from features.associations import models as associations
from features.contributions import forms as contributions


class Comment(contributions.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(core.forms.Submit('Kommentieren'))


class Update(forms.ModelForm):
    class Meta:
        model = associations.Association
        fields = ('public',)

    text = forms.CharField(widget=forms.Textarea())
    title = forms.CharField()

    def __init__(self, **kwargs):
        self.author = kwargs.pop('author')
        super().__init__(**kwargs)
        if self.instance.public or not self.instance.entity.is_group:
            del self.fields['public']

    def save(self, commit=True):
        association = super().save(commit)
        association.container.title = self.cleaned_data['title']
        association.container.save()
        association.container.versions.create(author=self.author, text=self.cleaned_data['text'])
        return association
