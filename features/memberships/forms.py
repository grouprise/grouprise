from django import forms

from . import models


class Apply(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = []

    def __init__(self, **kwargs):
        self.contribution = kwargs.pop('contribution')
        super().__init__(**kwargs)

    def save(self, commit=True):
        application = super().save(commit)
        self.contribution.contribution = application
        if commit:
            self.contribution.save()
        return application
