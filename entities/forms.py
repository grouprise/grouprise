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

from features.gestalten import models
from crispy_forms import bootstrap, layout
from django import forms
from django.contrib.auth import models as auth_models
from django.contrib.sites import models as sites_models
from utils import forms as utils_forms


class User(utils_forms.FormMixin, forms.ModelForm):
    class Meta:
        fields = ('first_name', 'last_name', 'username')
        labels = {'username': 'Adresse der Benutzerseite / Pseudonym'}
        model = auth_models.User


class Gestalt(utils_forms.ExtraFormMixin, forms.ModelForm):
    extra_form_class = User

    class Meta:
        fields = ('about', 'public')
        model = models.Gestalt

    def get_instance(self):
        return self.instance.user

    def get_layout(self):
        DOMAIN = sites_models.Site.objects.get_current().domain
        return (
                bootstrap.PrependedText(
                    'username',
                    '%(domain)s/gestalt/' % {'domain': DOMAIN}),
                'first_name',
                'last_name',
                layout.Field('about', rows=5),
                'public',
                utils_forms.Submit('Profil ändern'),
                )


class GroupFilter(utils_forms.FormMixin, forms.Form):
    name = forms.CharField()
    inline = True
    layout = ('name', utils_forms.Submit('Gruppen filtern', field_classes='btn btn-default'))
    method = 'GET'
