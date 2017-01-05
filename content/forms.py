from . import models
from crispy_forms import layout
from django import forms
from django.core import urlresolvers
from entities import models as entities
from features.gestalten import models as gestalten
from features.groups import models as groups
from utils import forms as utils_forms


class BaseContent(utils_forms.FormMixin, forms.ModelForm):
    author = forms.ModelChoiceField(
            disabled=True, queryset=gestalten.Gestalt.objects.all(),
            widget=forms.HiddenInput)
    pinned = forms.BooleanField(label='Im Intro der Gruppe anheften', required=False)
    images = forms.ModelMultipleChoiceField(
            queryset=models.Image.objects.filter(content__isnull=True), required=False,
            widget=forms.MultipleHiddenInput)

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super().__init__(*args, **kwargs)
        if self.author is None:
            self.author = gestalten.Gestalt.objects.get(pk=self.initial['author'])
        self.fields['group'] = forms.ModelChoiceField(
                label='Gruppe', queryset=self.get_group_queryset(), required=False)

    def get_group_queryset(self):
        return groups.Group.objects.filter(memberships__member=self.author)

    def save(self):
        content = super().save()
        if self.author != self.instance.author:
            self.instance.add_to_additional_authors(self.author)
            self.instance.save()
        for image in self.cleaned_data['images']:
            image.content = content
            image.save()
        if self.cleaned_data['group']:
            entities.GroupContent.objects.update_or_create(
                    content=content, group=self.cleaned_data['group'],
                    defaults={'pinned': self.cleaned_data['pinned']})
        else:
            entities.GroupContent.objects.filter(content=content).delete()
        return content


class Article(BaseContent):
    layout = (
            'author', 'group', 'title', utils_forms.EditorField('text'), 'pinned', 'public',
            utils_forms.Submit('Artikel erstellen'), 'images')

    class Meta:
        fields = ('author', 'public', 'text', 'title')
        model = models.Article


class Event(BaseContent):
    layout = (
            'author', 'group', 'pinned', 'title',
            layout.Field('time', data_component='date date-datetime'),
            layout.Field('until_time', data_component='date date-datetime'),
            'all_day', 'place', utils_forms.EditorField('text'), 'public',
            utils_forms.Submit('Ereignis erstellen'), 'images')

    class Meta:
        fields = ('all_day', 'author', 'place', 'public', 'text', 'time', 'title', 'until_time')
        labels = {'text': 'Beschreibung'}
        model = models.Event


class Gallery(BaseContent):
    image_creation_redirect = forms.BooleanField(required=False, widget=forms.HiddenInput)
    layout = (
            'image_creation_redirect', 'author', 'group', 'title', utils_forms.EditorField('text'),
            'public', 'pinned', utils_forms.Submit('Galerie erstellen'), 'images')

    class Meta:
        fields = ('author', 'public', 'text', 'title')
        labels = {'text': 'Beschreibung'}
        model = models.Gallery

    def get_helper(self):
        helper = super().get_helper()
        helper.form_action = urlresolvers.reverse('gallery-create')
        return helper


class ContentUpdate(utils_forms.FormMixin, forms.ModelForm):
    class Meta:
        fields = ('text', 'title')
        model = models.Content

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author')
        self.groupcontent = kwargs.pop('groupcontent', None)
        super().__init__(*args, **kwargs)
        if self.groupcontent:
            self.fields['pinned'] = forms.BooleanField(
                    label='Im Intro der Gruppe anheften', required=False)
            self.initial['pinned'] = self.groupcontent.pinned

    def get_layout(self):
        fields = layout.Layout(
                'title', utils_forms.EditorField('text'), utils_forms.Submit('Beitrag ändern'))
        if self.groupcontent:
            fields.insert(-1, 'pinned')
        return fields

    def save(self):
        if self.author != self.instance.author:
            self.instance.add_to_additional_authors(self.author)
        if self.groupcontent:
            self.groupcontent.pinned = self.cleaned_data['pinned']
            self.groupcontent.save()
        return super().save()
