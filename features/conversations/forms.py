from crispy_forms import helper, layout
from django import forms
from features.texts import models as texts


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
