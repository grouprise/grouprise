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
    text = forms.CharField(label='Text', widget=core.forms.EditorTextarea)
    title = forms.CharField(label='Titel')
    image = forms.ModelChoiceField(
            label='Beitragsbild', queryset=None, required=False,
            widget=forms.Select(attrs={'data-component': 'image-picker'}),
            help_text='Das Beitragsbild wird beispielsweise auf Übersichtsseiten in der '
            'Vorschau des Beitrags angezeigt.')

    place = forms.CharField(label='Veranstaltungsort / Anschrift', max_length=255)
    time = forms.DateTimeField(label='Beginn')
    until_time = forms.DateTimeField(label='Ende', required=False)
    all_day = forms.BooleanField(
            label='ganztägig', help_text='Die Veranstaltung dauert den ganzen Tag.',
            required=False)

    def __init__(self, **kwargs):
        self.author = kwargs.pop('author')
        with_time = kwargs.pop('with_time')
        super().__init__(**kwargs)
        self.fields['image'].queryset = self.author.images
        if self.instance.entity.is_group:
            del self.fields['group']
        else:
            self.fields['group'].queryset = groups.Group.objects.filter(
                    memberships__member=self.author)
        if not with_time:
            del self.fields['place']
            del self.fields['time']
            del self.fields['until_time']
            del self.fields['all_day']
        else:
            del self.fields['image']

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
            self.instance.container = models.Content.objects.create(
                    title=self.cleaned_data['title'],
                    image=self.cleaned_data.get('image'),
                    place=self.cleaned_data.get('place', ''),
                    time=self.cleaned_data.get('time'),
                    until_time=self.cleaned_data.get('until_time'),
                    all_day=self.cleaned_data.get('all_day', False))
            self.instance.container.versions.create(
                    author=self.author, text=self.cleaned_data['text'])
            self.save_content_relations(commit)
            return super().save(commit)

    def save_content_relations(self, commit):
        pass


class Update(forms.ModelForm):
    class Meta:
        model = associations.Association
        fields = ('pinned', 'public', 'slug')

    title = forms.CharField(label='Titel')
    text = forms.CharField(label='Text', widget=core.forms.EditorTextarea())
    image = forms.ModelChoiceField(
            label='Beitragsbild', queryset=None, required=False,
            widget=forms.Select(attrs={'data-component': 'image-picker'}),
            help_text='Das Beitragsbild wird beispielsweise auf Übersichtsseiten in der '
            'Vorschau des Beitrags angezeigt.')

    place = forms.CharField(label='Veranstaltungsort / Anschrift', max_length=255)
    time = forms.DateTimeField(label='Beginn')
    until_time = forms.DateTimeField(label='Ende', required=False)
    all_day = forms.BooleanField(
            label='ganztägig', help_text='Die Veranstaltung dauert den ganzen Tag.',
            required=False)

    def __init__(self, **kwargs):
        self.author = kwargs.pop('author')
        super().__init__(**kwargs)
        self.fields['image'].queryset = self.author.images
        if not self.instance.entity.is_group:
            del self.fields['pinned']
        if self.instance.public:
            del self.fields['public']
        if not self.initial['time']:
            del self.fields['place']
            del self.fields['time']
            del self.fields['until_time']
            del self.fields['all_day']
        else:
            del self.fields['image']

    def clean_slug(self):
        q = associations.Association.objects.filter(
                entity_type=self.instance.entity_type, entity_id=self.instance.entity_id,
                slug=self.cleaned_data['slug'])
        if q.exists() and q.get() != self.instance:
            raise forms.ValidationError('Der Kurzname ist bereits vergeben.', code='unique')
        return self.cleaned_data['slug']

    def save(self, commit=True):
        association = super().save(commit)
        association.container.title = self.cleaned_data['title']
        association.container.image = self.cleaned_data.get('image')
        if self.initial['time']:
            association.container.place = self.cleaned_data['place']
            association.container.time = self.cleaned_data['time']
            association.container.until_time = self.cleaned_data['until_time']
            association.container.all_day = self.cleaned_data['all_day']
        association.container.save()
        association.container.versions.create(author=self.author, text=self.cleaned_data['text'])
        self.save_content_relations(commit)
        return association

    def save_content_relations(self, commit):
        pass
