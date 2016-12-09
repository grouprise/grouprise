from . import models
from crispy_forms import helper, layout
from django import forms
from features.associations import models as associations
from features.texts import models as texts


class Create(forms.ModelForm):
    subject = forms.CharField(label='Thema', max_length=255)
    text = forms.CharField(label='Nachricht', widget=forms.Textarea)

    class Meta:
        model = associations.Association
        fields = []

    def __init__(self, *args, **kwargs):
        self.text = kwargs.pop('text')
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
                'subject',
                layout.Field('text', data_component='editor'),
                layout.Submit('create', 'Nachricht senden'))

    def save(self, commit=True):
        conversation = models.Conversation.objects.create(subject=self.cleaned_data['subject'])
        self.text.container = conversation
        self.text.text = self.cleaned_data['text']
        self.text.save()
        self.instance.container = conversation
        return super().save(commit)


class Reply(forms.ModelForm):
    class Meta:
        model = texts.Text
        fields = ('text',)
        labels = {'text': 'Antwort'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = layout.Layout(
                layout.Field('text', data_component='editor'),
                layout.Submit('reply', 'Antworten'))
