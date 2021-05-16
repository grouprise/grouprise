from django import forms
from django.utils.translation import gettext as _


class MatrixChatGestaltSettingsForm(forms.Form):
    matrix_id = forms.RegexField(
        # see https://matrix.org/docs/spec/appendices#user-identifiers
        r"^(@[\w.=\-/]+:[\w.-]+\.[a-zA-Z]{2,}|)$",
        required=False,
        strip=True,
        label=_("Custom (external) matrix user ID"),
        widget=forms.TextInput(),
        help_text=_(
            "Leave this field empty, if you want to use the local Matrix user ID. "
            "A Matrix user ID looks like '@foo:example.org'."
        ),
    )
