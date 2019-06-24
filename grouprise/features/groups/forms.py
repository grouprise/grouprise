from django import forms
from django.contrib.contenttypes import models as contenttypes
from django.contrib.sites.models import Site
from taggit.forms import TextareaTagWidget

from grouprise.features.tags import models as tags
from . import models


class RecommendForm(forms.Form):
    recipients = forms.CharField(
        label='E-Mail-Adressen oder Gestalten', widget=forms.Textarea({'rows': 3}),
        help_text='E-Mail-Adressen oder Gestalten (@kurzname) durch Komma, Leerzeichen '
        'oder Zeilenumbruch getrennt'
    )
    text = forms.CharField(label='Empfehlungstext', widget=forms.Textarea({'rows': 14}))


class Update(forms.ModelForm):
    class Meta:
        fields = (
                'address', 'closed', 'description', 'date_founded', 'name', 'slug', 'tags', 
                'url', 'url_import_feed')
        model = models.Group
        widgets = {
                'address': forms.Textarea({'rows': 3}),
                'date_founded': forms.DateInput({'data-component': 'date'}),
                'description': forms.Textarea({'rows': 5}),
                'tags': TextareaTagWidget({'rows': 2}),
                }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slug_domain = '{}/'.format(Site.objects.get_current().domain)
