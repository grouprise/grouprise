from django import forms

from grouprise.features.gestalten.models import Gestalt
from grouprise.features.memberships.models import Membership
from . import models


class Apply(forms.ModelForm):
    class Meta:
        model = models.Application
        fields = []

    def __init__(self, **kwargs):
        self.contribution = kwargs.pop("contribution")
        super().__init__(**kwargs)

    def save(self, commit=True):
        application = super().save(commit)
        self.contribution.contribution = application
        if commit:
            self.contribution.save()
        return application


class CreateMembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = []

    member_email = forms.EmailField(label="E-Mail-Adresse")

    def save(self, commit=True):
        member = Gestalt.objects.get_or_create_by_email(
            self.cleaned_data["member_email"]
        )
        self.instance.member = member
        return super().save(commit)


class Request(forms.Form):
    member = forms.EmailField(label="E-Mail-Adresse")
