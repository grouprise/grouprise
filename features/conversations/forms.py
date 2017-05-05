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

from . import models
from crispy_forms import helper, layout
from django import forms
from features.gestalten import models as gestalten
from features.associations import models as associations
from features.contributions import forms as contributions, models as contributions_models
from utils import forms as utils_forms


class Create(forms.ModelForm):
    author = forms.EmailField(label='E-Mail-Adresse')
    subject = forms.CharField(label='Thema', max_length=255)
    text = forms.CharField(label='Nachricht', widget=forms.Textarea)

    class Meta:
        model = associations.Association
        fields = []

    def __init__(self, *args, **kwargs):
        self.has_author = kwargs.pop('has_author')
        self.contribution = kwargs.pop('contribution')
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
                'subject',
                layout.Field('text', rows=5),
                layout.Submit('create', 'Nachricht senden'))
        if self.has_author:
            del self.fields['author']
        else:
            self.helper.layout.insert(0, 'author')

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
        # contribution creation)
        self.contribution.container = conversation
        self.contribution.contribution = contributions_models.Text.objects.create(
                text=self.cleaned_data['text'])
        if 'author' in self.cleaned_data:
            self.contribution.author = gestalten.Gestalt.get_or_create(
                    self.cleaned_data['author'])
        self.contribution.save()

        return association


class Reply(contributions.Text):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(utils_forms.Submit('Antworten'))
