from django import forms
from django.utils.translation import gettext as _
from taggit.forms import TagField, TextareaTagWidget

from grouprise.core.settings import get_grouprise_site

from . import models


class RecommendForm(forms.Form):
    recipients = forms.CharField(
        label="E-Mail-Adressen oder Gestalten",
        widget=forms.Textarea({"rows": 3}),
        help_text="E-Mail-Adressen oder Gestalten (@kurzname) durch Komma, Leerzeichen "
        "oder Zeilenumbruch getrennt",
    )
    text = forms.CharField(label="Empfehlungstext", widget=forms.Textarea({"rows": 14}))


class Update(forms.ModelForm):
    tags = TagField(
        widget=TextareaTagWidget({"rows": 2}),
        help_text=_("A comma-separated list of tags that best describe your group."),
    )

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug_domain = "{}/".format(get_grouprise_site().domain)
