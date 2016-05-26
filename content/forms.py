from . import models
from crispy_forms import layout
from django import forms
from entities import models as entities_models
from utils import forms as utils_forms


class BaseContent(utils_forms.FormMixin, forms.ModelForm):
    author = forms.ModelChoiceField(disabled=True, queryset=entities_models.Gestalt.objects.all(), widget=forms.HiddenInput)
    pinned = forms.BooleanField(label='Im Intro der Gruppe anheften', required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'] = forms.ModelChoiceField(label='Gruppe', queryset=self.get_group_queryset(), required=False)

    def get_group_queryset(self):
        return entities_models.Gestalt.objects.get(pk=self.initial['author']).groups

    def save(self):
        content = super().save()
        if self.cleaned_data['group']:
            entities_models.GroupContent.objects.create(content=content, group=self.cleaned_data['group'], pinned=self.cleaned_data['pinned'])
        return content


class Article(BaseContent):
    layout = ('author', 'group', 'title', utils_forms.EditorField('text'), 'pinned', utils_forms.Submit('Artikel erstellen'))

    class Meta:
        fields = ('author', 'text', 'title')
        model = models.Article

    def __init__(self, *args, **kwargs):
        kwargs['instance'] = models.Article(public=True)
        super().__init__(*args, **kwargs)


class Event(BaseContent):
    layout = ('author', 'group', 'title', 'time', 'place', utils_forms.EditorField('text'), 'public', 'pinned', utils_forms.Submit('Ereignis erstellen'))

    class Meta:
        fields = ('author', 'place', 'public', 'text', 'time', 'title')
        model = models.Event


class Gallery(BaseContent):
    layout = ('author', 'group', 'title', utils_forms.EditorField('text'), 'public', 'pinned', utils_forms.Submit('Galerie erstellen'))

    class Meta:
        fields = ('author', 'public', 'text', 'title')
        labels = {'text': 'Beschreibung'}
        model = models.Gallery


class BaseMessage(utils_forms.FormMixin, forms.ModelForm):
    layout = ('sender', 'recipient', 'title', utils_forms.EditorField('text'), utils_forms.Submit('Nachricht senden'))
    sender = forms.EmailField(disabled=True, widget=forms.HiddenInput)

    class Meta:
        fields = ('text', 'title')
        labels = {'text': 'Nachricht', 'title': 'Betreff'}
        model = models.Article

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['recipient'] = forms.ModelChoiceField(disabled=True, label='Empfängerin', queryset=self.get_recipient_queryset())

    def save(self):
        message = super().save(commit=False)
        message.author = entities_models.Gestalt.objects.get(user__email=self.cleaned_data['sender'])
        message.save()
        return message


class GestaltMessage(BaseMessage):
    def get_recipient_queryset(self):
        return entities_models.Gestalt.objects.all()

    def save(self):
        message = super().save()
        entities_models.GestaltContent.objects.create(content=message, gestalt=self.cleaned_data['recipient'])

class GroupMessage(BaseMessage):
    def get_recipient_queryset(self):
        return entities_models.Group.objects.all()

    def save(self):
        message = super().save()
        entities_models.GroupContent.objects.create(content=message, group=self.cleaned_data['recipient'])
