from django import forms
from django.utils.translation import gettext as _

from grouprise.core.settings import get_grouprise_site
from grouprise.features.tags.forms import FeaturedTagInputField

from . import models
from ..tags.settings import TAG_SETTINGS


class CreateForm(forms.ModelForm):
    tags = FeaturedTagInputField("group-tags", required=False)

    class Meta:
        model = models.Group
        fields = ["name", "tags"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if TAG_SETTINGS.MIN_FEATURED_GROUP_TAG_COUNT == 0:
            del self.fields["tags"]


class RecommendForm(forms.Form):
    recipients = forms.CharField(
        label="E-Mail-Adressen oder Gestalten",
        widget=forms.Textarea({"rows": 3}),
        help_text="E-Mail-Adressen oder Gestalten (@kurzname) durch Komma, Leerzeichen "
        "oder Zeilenumbruch getrennt",
    )
    text = forms.CharField(label="Empfehlungstext", widget=forms.Textarea({"rows": 14}))


class Update(forms.ModelForm):
    tags = FeaturedTagInputField("group-tags", required=False)

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
        }
        help_texts = {
            "tags": _("A comma-separated list of tags that best describe your group."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug_domain = "{}/".format(get_grouprise_site().domain)
