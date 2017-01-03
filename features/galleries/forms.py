"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from django import forms
from django.db.models import Q

from features.content import forms as content
from features.images import models as images


class Create(content.Create):
    text = forms.CharField(label='Beschreibung', widget=forms.Textarea({'rows': 2}))
    images = forms.ModelMultipleChoiceField(
            label='Bilder', queryset=None, widget=forms.SelectMultiple(attrs={'size': 10}))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields['images'].queryset = self.author.images

    def save(self, commit=True):
        association = super().save(commit)
        for image in self.cleaned_data['images']:
            association.container.gallery_images.create(image=image)
        return association


class Update(content.Update):
    text = forms.CharField(label='Beschreibung', widget=forms.Textarea({'rows': 2}))
    images = forms.ModelMultipleChoiceField(
            label='Bilder', queryset=None, widget=forms.SelectMultiple(attrs={'size': 10}))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_image_pks = self.instance.container.gallery_images.values_list(
                'image__pk', flat=True)
        self.fields['images'].queryset = images.Image.objects.filter(
                Q(pk__in=self.initial_image_pks) | Q(creator=self.author))
        self.initial['images'] = images.Image.objects.filter(
                pk__in=self.initial_image_pks)

    def save(self, commit=True):
        association = super().save(commit)
        chosen_image_pks = self.cleaned_data['images'].values_list('pk', flat=True)
        for gallery_image in association.container.gallery_images.all():
            if gallery_image.image.pk not in chosen_image_pks:
                gallery_image.delete()
        for image in self.cleaned_data['images']:
            if image.pk not in self.initial_image_pks:
                association.container.gallery_images.create(image=image)
        return association
