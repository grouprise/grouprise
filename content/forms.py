from . import models
from allauth.account import adapter as allauth_adapter
from crispy_forms import layout
from django import forms
from django.contrib import auth
from django.core import urlresolvers
from entities import models as entities_models
from features.groups import models as groups
from utils import forms as utils_forms


class BaseContent(utils_forms.FormMixin, forms.ModelForm):
    author = forms.ModelChoiceField(
            disabled=True, queryset=entities_models.Gestalt.objects.all(),
            widget=forms.HiddenInput)
    pinned = forms.BooleanField(label='Im Intro der Gruppe anheften', required=False)
    images = forms.ModelMultipleChoiceField(
            queryset=models.Image.objects.filter(content__isnull=True), required=False,
            widget=forms.MultipleHiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'] = forms.ModelChoiceField(
                label='Gruppe', queryset=self.get_group_queryset(), required=False)

    def get_group_queryset(self):
        return groups.Group.objects.filter(memberships__member=self.initial['author'])

    def save(self):
        content = super().save()
        for image in self.cleaned_data['images']:
            image.content = content
            image.save()
        if self.cleaned_data['group']:
            entities_models.GroupContent.objects.update_or_create(
                    content=content, group=self.cleaned_data['group'],
                    defaults={'pinned': self.cleaned_data['pinned']})
        else:
            entities_models.GroupContent.objects.filter(content=content).delete()
        return content


class Article(BaseContent):
    layout = (
            'author', 'group', 'title', utils_forms.EditorField('text'), 'pinned',
            utils_forms.Submit('Artikel erstellen'), 'images')

    class Meta:
        fields = ('author', 'text', 'title')
        model = models.Article

    def __init__(self, *args, **kwargs):
        kwargs['instance'] = models.Article(public=True)
        super().__init__(*args, **kwargs)


class Event(BaseContent):
    layout = (
            'author', 'group', 'pinned', 'title',
            layout.Field('time', data_component='date date-datetime'),
            'place', utils_forms.EditorField('text'), 'public',
            utils_forms.Submit('Ereignis erstellen'), 'images')

    class Meta:
        fields = ('author', 'place', 'public', 'text', 'time', 'title')
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


class BaseMessage(utils_forms.FormMixin, forms.ModelForm):
    layout = (
            'recipient', 'sender', 'title', utils_forms.EditorField('text'),
            utils_forms.Submit('Nachricht senden'))
    sender = forms.EmailField(label='E-Mail-Adresse')

    class Meta:
        fields = ('text', 'title')
        labels = {'text': 'Nachricht', 'title': 'Betreff'}
        model = models.Article

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'] = forms.ModelChoiceField(
                disabled=True, label='Empfängerin', queryset=self.get_recipient_queryset(),
                widget=forms.HiddenInput)
        if self.initial.get('sender'):
            self.fields['sender'].disabled = True
            self.helper['sender'].wrap(layout.Field, type='hidden')

    def clean(self):
        if not self.fields['sender'].disabled and 'sender' in self.cleaned_data:
            try:
                user = auth.get_user_model().objects.get(email=self.cleaned_data['sender'])
                if user.has_usable_password():
                    self.add_error('sender', forms.ValidationError(
                        'Es gibt bereits ein Benutzerkonto mit dieser E-Mail-Adresse. Bitte melde '
                        'Dich mit E-Mail-Adresse und Kennwort an.', code='existing'))
            except auth.get_user_model().DoesNotExist:
                pass
        return super().clean()

    def save(self):
        message = super().save(commit=False)
        user, created = auth.get_user_model().objects.get_or_create(
                email=self.cleaned_data['sender'])
        if created:
            allauth_adapter.get_adapter().populate_username(None, user)
            user.set_unusable_password()
            user.save()
        message.author = entities_models.Gestalt.objects.get(
                user__email=self.cleaned_data['sender'])
        message.save()
        return message


class GestaltMessage(BaseMessage):
    def get_recipient_queryset(self):
        return entities_models.Gestalt.objects.all()

    def save(self):
        message = super().save()
        entities_models.GestaltContent.objects.create(
                content=message, gestalt=self.cleaned_data['recipient'])


class GroupMessage(BaseMessage):
    def get_recipient_queryset(self):
        return groups.Group.objects.all()

    def save(self):
        message = super().save()
        entities_models.GroupContent.objects.create(
                content=message, group=self.cleaned_data['recipient'])


class ContentUpdate(utils_forms.FormMixin, forms.ModelForm):
    class Meta:
        fields = ('text', 'title')
        model = models.Content

    def __init__(self, *args, **kwargs):
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
        if self.groupcontent:
            self.groupcontent.pinned = self.cleaned_data['pinned']
            self.groupcontent.save()
        return super().save()
