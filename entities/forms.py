from . import models
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
        fields = ('about', 'avatar')
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
                'avatar',
                layout.Field('about', rows=5),
                utils_forms.Submit('Profileinstellungen ändern'),
                )

class GroupAttention(utils_forms.FormMixin, forms.ModelForm):
    attendee_email = forms.EmailField(disabled=True, widget=forms.HiddenInput)
    group = forms.ModelChoiceField(disabled=True, queryset=models.Group.objects.all(), widget=forms.HiddenInput)
    layout = ('attendee_email', 
            layout.HTML('<p>Möchtest Du per E-Mail benachrichtigt werden, '
                'wenn Mitglieder der Gruppe <em>{{ group }}</em> neue Beiträge '
                'veröffentlichen?</p>'),
            utils_forms.Submit('Benachrichtigungen erhalten'))

    class Meta:
        fields = ('group',)
        model = models.GroupAttention

    def save(self):
        attention = super().save(commit=False)
        attention.attendee = models.Gestalt.objects.get(user__email=self.cleaned_data['attendee_email'])
        attention.save()
        return attention
