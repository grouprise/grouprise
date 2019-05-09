import os

from django import forms

from grouprise.core.models import MAX_FILE_SIZE
from grouprise.features.content import forms as content


class Create(content.Create):
    text = forms.CharField(label='Beschreibung', widget=forms.Textarea({'rows': 2}))
    file = forms.FileField(
            label='Datei', help_text='Die maximal erlaubte Dateigröße beträgt {} MB.'.format(
                MAX_FILE_SIZE))

    def save(self, commit=True):
        association = super().save(False)
        association.container.versions.last().file.create(
                file=self.cleaned_data.get('file'),
                filename=os.path.basename(self.cleaned_data.get('file').name))
        if commit:
            association.save()
            self.send_post_create(association.container)
        return association


class Update(content.Update):
    text = forms.CharField(label='Beschreibung', widget=forms.Textarea({'rows': 2}))
    file = forms.FileField(
            label='Datei', help_text='Die maximal erlaubte Dateigröße beträgt {} MB.'.format(
                MAX_FILE_SIZE))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['file'] = self.instance.container.versions.last().file.get().file

    def save(self, commit=True):
        association = super().save(commit)
        association.container.versions.last().file.create(
                file=self.cleaned_data.get('file'),
                filename=os.path.basename(self.cleaned_data.get('file').name))
        return association
