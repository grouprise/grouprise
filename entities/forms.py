from crispy_forms import bootstrap, helper, layout
from django import forms as django_forms
from django.contrib.auth import models as auth_models
from django.contrib.sites import shortcuts


class User(django_forms.ModelForm):
    class Meta:
        model = auth_models.User
        fields = ['first_name', 'last_name', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Adresse der Benutzerseite / Pseudonym'

        self.helper = helper.FormHelper()
        self.helper.form_tag = False
        self.helper.layout = layout.Layout(*self.get_layout())
    
    def get_layout(self):
        DOMAIN = shortcuts.get_current_site(None).domain
        return [
                bootstrap.PrependedText('username', '%(domain)s/gestalt/' % {'domain': DOMAIN }),
                'first_name',
                'last_name',
                ]
