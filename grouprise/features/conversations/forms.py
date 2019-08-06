from django import forms

import grouprise.features
from grouprise.features.gestalten import models as gestalten
from grouprise.features.associations import models as associations
from grouprise.features.contributions import models as contributions_models
from grouprise.features.contributions.models import Contribution
from grouprise.features.memberships.models import Application
from . import models


class Create(forms.ModelForm):
    author = forms.EmailField(label='E-Mail-Adresse')
    subject = forms.CharField(label='Thema', max_length=255)
    text = forms.CharField(label='Nachricht', widget=forms.Textarea(
        {'rows': 5, 'data-component': 'keysubmit autosize'}))

    class Meta:
        model = associations.Association
        fields = []

    def __init__(self, *args, **kwargs):
        self.has_author = kwargs.pop('has_author')
        self.contribution = kwargs.pop('contribution')
        self.with_membership_application = kwargs.pop('with_membership_application')
        super().__init__(*args, **kwargs)
        if self.has_author:
            del self.fields['author']

    def clean(self):
        if 'author' in self.cleaned_data:
            try:
                gestalt = gestalten.Gestalt.objects.get(
                        user__email=self.cleaned_data['author'])
                if gestalt.user.has_usable_password():
                    self.add_error('author', forms.ValidationError(
                        'Es gibt bereits ein Benutzerkonto mit dieser E-Mail-Adresse. Bitte '
                        'melde Dich mit E-Mail-Adresse und Kennwort an.', code='existing'))
            except gestalten.Gestalt.DoesNotExist:
                pass
        return super().clean()

    def save(self, commit=True):
        # create conversation
        conversation = models.Conversation.objects.create(subject=self.cleaned_data['subject'])

        # create association
        self.instance.container = conversation
        association = super().save(commit)

        # create initial contribution (after the association, notifications are sent on
        # contribution creation signal)
        self.contribution.container = conversation
        self.contribution.contribution = contributions_models.Text.objects.create(
                text=self.cleaned_data['text'])
        if 'author' in self.cleaned_data:
            self.contribution.author = gestalten.Gestalt.objects.get_or_create_by_email(
                    self.cleaned_data['author'])
        self.contribution.save()

        # create membership application for closed groups
        if self.with_membership_application:
            application = Application.objects.create(
                    group=association.entity, attached_to=self.contribution)
            application_contribution = Contribution(author=self.contribution.author)
            application_contribution.container = conversation
            application_contribution.contribution = application
            application_contribution.save()

        # send contribution creation signal
        grouprise.features.contributions.signals.post_create.send(
                sender=self.__class__, instance=self.contribution)

        return association
