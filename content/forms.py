from . import models
from django import forms
from entities import models as entities_models
from util import forms as utils_forms

class Message(utils_forms.FormMixin, forms.ModelForm):
    layout = ('sender', 'recipient', 'title', 'text', utils_forms.Submit('Nachricht senden'))
    recipient = forms.ModelChoiceField(disabled=True, label='Empfängerin', queryset=entities_models.Group.objects.all())
    sender = forms.EmailField(disabled=True, widget=forms.HiddenInput)

    class Meta:
        fields = ('text', 'title')
        labels = {'text': 'Nachricht', 'title': 'Betreff'}
        model = models.Article

    def save(self):
        message = super().save(commit=False)
        message.author = entities_models.Gestalt.objects.get(user__email=self.cleaned_data['sender'])
        message.save()
        entities_models.GroupContent(content=message, group=self.cleaned_data['recipient']).save()
