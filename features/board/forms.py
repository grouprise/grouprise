from django import forms

from . import models


class Create(forms.ModelForm):
    class Meta:
        fields = ('text',)
        model = models.Note
