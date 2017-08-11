import os

import django
from django import forms

from features.content import forms as content


class Create(content.Create):
    text = forms.CharField(label='Beschreibung', widget=forms.Textarea({'rows': 2}))
    file = forms.FileField(
            label='Datei', help_text='Die maximal erlaubte Dateigröße beträgt {} MB.'.format(
                django.conf.settings.MAX_FILE_SIZE // (1024 * 1024)))

    def save(self, commit=True):
        association = super().save(False)
        association.container.versions.first().file.create(
                file=self.cleaned_data.get('file'),
                filename=os.path.basename(self.cleaned_data.get('file').name))
        if commit:
            association.save()
        return association
