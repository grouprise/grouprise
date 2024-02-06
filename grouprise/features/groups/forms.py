from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from taggit.forms import TextareaTagWidget
from taggit.models import Tag

from grouprise.core.settings import get_grouprise_site

from . import models
from ..tags.settings import TAG_SETTINGS


class RecommendForm(forms.Form):
    recipients = forms.CharField(
        label="E-Mail-Adressen oder Gestalten",
        widget=forms.Textarea({"rows": 3}),
        help_text="E-Mail-Adressen oder Gestalten (@kurzname) durch Komma, Leerzeichen "
        "oder Zeilenumbruch getrennt",
    )
    text = forms.CharField(label="Empfehlungstext", widget=forms.Textarea({"rows": 14}))


class Update(forms.ModelForm):
    class Meta:
        fields = (
            "address",
            "closed",
            "description",
            "date_founded",
            "name",
            "slug",
            "tags",
            "url",
            "url_import_feed",
        )
        model = models.Group
        widgets = {
            "address": forms.Textarea({"rows": 3}),
            "date_founded": forms.DateInput({"data-component": "date"}),
            "description": forms.Textarea({"rows": 5}),
            "tags": TextareaTagWidget({"rows": 2}),
        }
        help_texts = {
            "tags": _("A comma-separated list of tags that best describe your group."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug_domain = "{}/".format(get_grouprise_site().domain)

    def clean_tags(self):
        tags = self.cleaned_data["tags"]
        tag_count = (
            Tag.objects.filter(name__in=tags)
            .filter(id__in=TAG_SETTINGS.FEATURED_TAG_IDS)
            .count()
        )
        min_tag_count = TAG_SETTINGS.MIN_FEATURED_GROUP_TAG_COUNT
        if tag_count < min_tag_count:
            raise ValidationError(
                _("At least %d featured tags need to be specified.") % min_tag_count
            )
        return tags
