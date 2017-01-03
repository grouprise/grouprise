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

from crispy_forms import helper, layout
from django import forms
from features.contributions import models as contributions


class Text(forms.ModelForm):
    text = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = contributions.Contribution
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_show_labels = False
        self.helper.layout = layout.Layout(
                layout.Field('text', rows=3, **{
                    'data-component': 'keysubmit autosize cite cite-sink'
                }))

    def save(self, commit=True):
        contribution = super().save(False)
        contribution.contribution = contributions.Text.objects.create(
                text=self.cleaned_data['text'])
        if commit:
            contribution.save()
        return contribution
