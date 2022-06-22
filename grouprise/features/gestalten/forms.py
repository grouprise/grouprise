import allauth
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError

from grouprise.core.forms import CaptchaField
from grouprise.features.gestalten import models
from grouprise.features.stadt.forms import validate_entity_slug

username_validators = [validate_entity_slug]


class GestaltByEmailField(forms.EmailField):
    default_error_messages = {
        "login": "Es gibt bereits ein Benutzerkonto mit dieser E-Mail-Adresse. Bitte melde "
        "Dich mit E-Mail-Adresse und Kennwort an."
    }

    def __init__(self, *args, **kwargs):
        # This field is used in place of a ModelChoiceField implementation
        # and django pre-populates kwargs based on the foreign key relation.
        # As forms.EmailField is not a ModelChoiceField subclass it will not
        # recognize the specialized keyword arguments and raise an error.
        # TODO: this seems like a hack and there’s probably a better way to
        #       define a simple form field for a relation field.
        for key in ["blank", "limit_choices_to", "queryset", "to_field_name"]:
            kwargs.pop(key, None)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        value = super().clean(value)
        gestalt = models.Gestalt.objects.get_or_create_by_email(value)
        if gestalt.can_login():
            raise ValidationError(self.error_messages["login"], code="login")
        return gestalt


class Create(allauth.account.forms.SignupForm):
    password1 = forms.CharField(label="Kennwort", widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Kennwort (Wiederholung)", widget=forms.PasswordInput()
    )
    captcha = CaptchaField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"] = forms.EmailField(label="E-Mail-Adresse")

    def clean_email(self):
        try:
            return super().clean_email()
        except forms.ValidationError as e:
            try:
                user = auth.get_user_model().objects.get(
                    email=self.cleaned_data["email"]
                )
                if user.has_usable_password():
                    raise e
            except auth.get_user_model().DoesNotExist:
                raise e
        return self.cleaned_data["email"]

    def save(self, request):
        try:
            adapter = allauth.account.adapter.get_adapter(request)
            user = auth.get_user_model().objects.get(email=self.cleaned_data["email"])
            adapter.set_password(user, self.cleaned_data["password1"])
            allauth.account.utils.setup_user_email(request, user, [])
            return user
        except auth.get_user_model().DoesNotExist:
            return super().save(request)


class Update(forms.ModelForm):
    class Meta:
        model = models.Gestalt
        fields = ("about", "public")
        widgets = {"about": forms.Textarea({"rows": 5})}

    first_name = forms.CharField(label="Vorname", required=False)
    last_name = forms.CharField(label="Nachname", required=False)
    slug = forms.SlugField(
        label="Pseudonym",
        help_text="Nur Buchstaben, Ziffern, Unter- und Bindestriche. "
        "Keine Umlaute, ß oder andere Sonderzeichen.",
    )

    def clean_slug(self):
        slug = self.cleaned_data["slug"]
        validate_entity_slug(slug, self.instance)
        return slug

    def get_instance(self):
        return self.instance.user

    def save(self, commit=True):
        self.instance.user.first_name = self.cleaned_data["first_name"]
        self.instance.user.last_name = self.cleaned_data["last_name"]
        self.instance.user.username = self.cleaned_data["slug"]
        if commit:
            self.instance.user.save()
        return super().save(commit)


class UpdateEmail(allauth.account.forms.AddEmailForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "E-Mail-Adresse"
        del self.fields["email"].widget.attrs["placeholder"]


class UpdatePassword(allauth.account.forms.ChangePasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["oldpassword"].label = "Aktuelles Kennwort"
        self.fields["password1"].label = "Neues Kennwort"
        self.fields["password2"].label = "Neues Kennwort (Wiederholung)"
        del self.fields["oldpassword"].widget.attrs["placeholder"]
        del self.fields["password1"].widget.attrs["placeholder"]
        del self.fields["password2"].widget.attrs["placeholder"]


class UpdatePasswordSet(allauth.account.forms.SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Kennwort"
        self.fields["password2"].label = "Kennwort (Wiederholung)"


class UpdatePasswordKey(allauth.account.forms.ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Kennwort"
        self.fields["password2"].label = "Kennwort (Wiederholung)"
