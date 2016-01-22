from crispy_forms import helper
from django import forms as django_forms
from django.contrib.auth import models as auth_models


class User(django_forms.ModelForm):
    class Meta:
        model = auth_models.User
        fields = ['username']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_tag = False
