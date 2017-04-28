from django import forms

from features.content import forms as content


class Create(content.Create):
    text = forms.CharField(label='Beschreibung', widget=forms.Textarea({'rows': 2}))
