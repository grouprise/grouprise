from . import models
from django import forms
from entities import models as entities_models
from utils import forms as utils_forms

class Article(utils_forms.FormMixin, forms.ModelForm):
    author = forms.ModelChoiceField(disabled=True, queryset=entities_models.Gestalt.objects.all(), widget=forms.HiddenInput)
    layout = ('author', 'title', 'text', utils_forms.Submit('Artikel erstellen'))

    class Meta:
        fields = ('author', 'text', 'title')
        model = models.Article

    def __init__(self, *args, **kwargs):
        kwargs['instance'] = models.Article(public=True)
        super().__init__(*args, **kwargs)

class BaseMessage(utils_forms.FormMixin, forms.ModelForm):
    layout = ('sender', 'recipient', 'title', 'text', utils_forms.Submit('Nachricht senden'))
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
