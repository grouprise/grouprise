from crispy_forms import helper, layout
from django import forms
from features.contributions import models as contributions


class Text(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = contributions.Contribution
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = layout.Layout(
                layout.Field('text', rows=3, **{
                    'data-component': 'keysubmit autosize cite cite-sink'
                }))

    def save(self, commit=True):
        contribution = super().save(False)
        contribution.contribution = contributions.Text.objects.create(
                text=self.cleaned_data['text'])
        if commit:
            contribution.save()
        return contribution
