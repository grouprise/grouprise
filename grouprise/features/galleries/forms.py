from django import forms
from django.db.models import Q

import grouprise.core
from grouprise.features.content import forms as content
from grouprise.features.images import models as images


class Create(content.Create):
    text = forms.CharField(label="Beschreibung", widget=forms.Textarea({"rows": 2}))
    images = forms.ModelMultipleChoiceField(
        label="Bilder",
        queryset=None,
        widget=forms.SelectMultiple(
            attrs={"size": 10, "data-component": "gallery-editor"}
        ),
        help_text=grouprise.core.models.IMAGE_FIELD_HELP_TEXT,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.fields["images"].queryset = self.author.images

    def save(self, commit=True):
        association = super().save(False)
        for image in self.cleaned_data["images"]:
            association.container.gallery_images.create(image=image)
        if commit:
            association.save()
            self.send_post_create(association.container)
        return association


class Update(content.Update):
    text = forms.CharField(label="Beschreibung", widget=forms.Textarea({"rows": 2}))
    images = forms.ModelMultipleChoiceField(
        label="Bilder",
        queryset=None,
        widget=forms.SelectMultiple(
            attrs={"size": 10, "data-component": "gallery-editor"}
        ),
        help_text=grouprise.core.models.IMAGE_FIELD_HELP_TEXT,
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.initial_image_pks = self.instance.container.gallery_images.values_list(
            "image__pk", flat=True
        )
        self.fields["images"].queryset = images.Image.objects.filter(
            Q(pk__in=self.initial_image_pks) | Q(creator=self.author)
        )
        self.initial["images"] = images.Image.objects.filter(
            pk__in=self.initial_image_pks
        )

    def save(self, commit=True):
        association = super().save(commit)
        chosen_image_pks = self.cleaned_data["images"].values_list("pk", flat=True)
        for gallery_image in association.container.gallery_images.all():
            if gallery_image.image.pk not in chosen_image_pks:
                gallery_image.delete()
        for image in self.cleaned_data["images"]:
            if image.pk not in self.initial_image_pks:
                association.container.gallery_images.create(image=image)
        return association
