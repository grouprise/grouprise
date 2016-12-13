from . import models
from crispy_forms import helper, layout
from django import forms
from entities import models as gestalten
from features.associations import models as associations
from features.texts import models as texts
from utils import forms as utils_forms


class Create(forms.ModelForm):
    author = forms.EmailField(label='E-Mail-Adresse')
    subject = forms.CharField(label='Thema', max_length=255)
    text = forms.CharField(label='Nachricht', widget=forms.Textarea)

    class Meta:
        model = associations.Association
        fields = []

    def __init__(self, *args, **kwargs):
        self.has_author = kwargs.pop('has_author')
        self.text = kwargs.pop('text')
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
                'subject',
                layout.Field('text', rows=5),
                layout.Submit('create', 'Nachricht senden'))
        if self.has_author:
            del self.fields['author']
        else:
            self.helper.layout.insert(0, 'author')

    def clean(self):
        if 'author' in self.cleaned_data:
            try:
                gestalt = gestalten.Gestalt.objects.get(
                        user__email=self.cleaned_data['author'])
                if gestalt.user.has_usable_password():
                    self.add_error('author', forms.ValidationError(
                        'Es gibt bereits ein Benutzerkonto mit dieser E-Mail-Adresse. Bitte '
                        'melde Dich mit E-Mail-Adresse und Kennwort an.', code='existing'))
            except gestalten.Gestalt.DoesNotExist:
                pass
        return super().clean()

    def save(self, commit=True):
        conversation = models.Conversation.objects.create(subject=self.cleaned_data['subject'])
        self.text.container = conversation
        self.text.text = self.cleaned_data['text']
        if 'author' in self.cleaned_data:
            self.text.author = gestalten.Gestalt.get_or_create(self.cleaned_data['author'])
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
                layout.Field('text', rows=3, **{'data-component': 'keysubmit'}),
                utils_forms.Submit('Antworten'))
