from django import forms
from django.contrib.gis.forms import PointField

from .models import Location


class LocationForm(forms.Form):
    point = PointField(widget=forms.HiddenInput({"data-location-input": ""}))

    class Meta:
        model = Location
        fields = {
            "point",
        }
