from django import forms
from django.db.models.functions import Lower


class TagGroup(forms.Form):
    
    group = forms.ModelChoiceField(label='Gruppe', queryset=None)

    def __init__(self, **kwargs):
        group_queryset = kwargs.pop('group_queryset')
        super().__init__(**kwargs)
        self.fields['group'].queryset = group_queryset
