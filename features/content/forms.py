import django.db.transaction
from django import forms

import core.forms
from . import models
from features.associations import models as associations
from features.contributions import forms as contributions
from features.groups import models as groups


class Comment(contributions.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(core.forms.Submit('Kommentieren'))


class Create(forms.ModelForm):
    class Meta:
        model = associations.Association
        fields = ('pinned', 'public')

    group = forms.ModelChoiceField(
            label='Veröffentlichen als', queryset=groups.Group.objects.none(), required=False,
            widget=core.forms.GroupSelect)
    text = forms.CharField(label='Text', widget=core.forms.EditorTextarea())
    title = forms.CharField(label='Titel')

    def __init__(self, **kwargs):
        self.author = kwargs.pop('author')
        super().__init__(**kwargs)
        if self.instance.entity.is_group:
            del self.fields['group']
        else:
            self.fields['group'].queryset = groups.Group.objects.filter(
                    memberships__member=self.author)

    def save(self, commit=True):
        with django.db.transaction.atomic():
            if not self.instance.entity.is_group and self.cleaned_data['group']:
                self.instance.entity = self.cleaned_data['group']
            self.instance.slug = core.models.get_unique_slug(
                    associations.Association, {
                        'entity_id': self.instance.entity_id,
                        'entity_type': self.instance.entity_type,
                        'slug': core.text.slugify(self.cleaned_data['title']),
                        })
            self.instance.container = models.Content.objects.create(title=self.cleaned_data['title'])
            self.instance.container.versions.create(author=self.author, text=self.cleaned_data['text'])
            return super().save(commit)


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
        if self.instance.public:
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
