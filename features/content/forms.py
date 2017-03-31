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
        fields = ('pinned', 'public', 'slug')

    text = forms.CharField(label='Text', widget=core.forms.EditorTextarea())
    title = forms.CharField(label='Titel')

    def __init__(self, **kwargs):
        self.author = kwargs.pop('author')
        super().__init__(**kwargs)
        if not self.instance.entity.is_group:
            del self.fields['pinned']
        if self.instance.public or not self.instance.entity.is_group:
            del self.fields['public']

    def clean_slug(self):
        if associations.Association.objects.filter(
                entity_type=self.instance.entity_type, entity_id=self.instance.entity_id,
                slug=self.cleaned_data['slug']).exists():
            raise forms.ValidationError('Der Kurzname ist bereits vergeben.', code='unique')
        return self.cleaned_data['slug']

    def save(self, commit=True):
        association = super().save(commit)
        association.container.title = self.cleaned_data['title']
        association.container.save()
        association.container.versions.create(author=self.author, text=self.cleaned_data['text'])
        return association
