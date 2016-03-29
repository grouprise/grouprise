from . import models
from django import forms
from entities import models as entities_models
from util import forms as utils_forms

class Message(utils_forms.FormMixin, forms.ModelForm):
    layout = ('title', 'text', utils_forms.Submit('Nachricht senden'))

    class Meta:
        fields = ('text', 'title')
        model = models.Article

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author')
        self.group = kwargs.pop('group')
        super().__init__(*args, **kwargs)
        self.fields['title'].label = 'Betreff'
        self.fields['text'].label = 'Nachricht'

    def save(self):
        self.instance.author = self.author
        message = super().save()
        entities_models.GroupContent(content=message, group=self.group).save()
