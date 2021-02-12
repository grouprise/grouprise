from django import forms

from grouprise.core.signals import post_create
from grouprise.features.contributions import models as contributions


class Text(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea({
        'rows': 3, 'data-component': 'keysubmit autosize cite cite-sink'}))

    class Meta:
        model = contributions.Contribution
        fields = ['in_reply_to']

    def __init__(self, *args, **kwargs):
        contributions = kwargs.pop('contributions')
        super().__init__(*args, **kwargs)
        self.fields['in_reply_to'].queryset = contributions
        self.fields['in_reply_to'].widget = forms.HiddenInput(
            {'data-component': 'cite cite-in-reply-to'})

    def save(self, commit=True):
        contribution = super().save(False)
        contribution.contribution = contributions.Text.objects.create(
                text=self.cleaned_data['text'])
        if commit:
            contribution.save()
        post_create.send(sender=self.__class__, instance=contribution)
        return contribution
