from crispy_forms import bootstrap
from django import forms
from django.contrib.auth import models as auth_models
from django.contrib.sites import shortcuts
from util import forms as util_forms

class User(util_forms.FormMixin, forms.ModelForm):
    class Meta:
        model = auth_models.User
        fields = ['first_name', 'last_name', 'username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Adresse der Benutzerseite / Pseudonym'

    def get_helper(self):
        helper = super.get_helper()
        helper.form_tag = False
        return helper
    
    def get_layout(self):
        DOMAIN = shortcuts.get_current_site(None).domain
        return [
                bootstrap.PrependedText('username', '%(domain)s/gestalt/' % {'domain': DOMAIN }),
                'first_name',
                'last_name',
                ]
