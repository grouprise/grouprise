from django import forms
from django.utils.translation import gettext as _

from .settings import MATRIX_SETTINGS

# see https://matrix.org/docs/spec/appendices#user-identifiers
MATRIX_USER_ID_REGEX = r"^(@[\w.=\-/]+:[\w.-]+\.[a-zA-Z]{2,}|)$"
MATRIX_ROOM_REFERENCE_REGEX = r"^([!#][\w.=\-/]+:[\w.-]+\.[a-zA-Z]{2,}|)$"
MATRIX_ROOM_REFERENCE_HELP = _(
    "A Matrix room ID (starting with '!') or an alias (starting with '#') can be used."
    " You may want to invite {bot_address} to this room and grant moderation power after"
    " changing the room address."
).format(bot_address=f"@{MATRIX_SETTINGS.BOT_USERNAME}:{MATRIX_SETTINGS.DOMAIN}")


class MatrixChatGestaltSettingsForm(forms.Form):
    matrix_id = forms.RegexField(
        MATRIX_USER_ID_REGEX,
        required=False,
        strip=True,
        label=_("Custom (external) matrix user ID"),
        widget=forms.TextInput(),
        help_text=_(
            "Leave this field empty, if you want to use the local Matrix user ID. "
            "A Matrix user ID looks like '@foo:example.org'."
        ),
    )


class MatrixChatGroupSettingsForm(forms.Form):
    room_public_visibility = forms.BooleanField(
        label=_("Show links to the public chat room"),
        required=False,
    )
    room_public_matrix_reference = forms.RegexField(
        MATRIX_ROOM_REFERENCE_REGEX,
        required=True,
        strip=True,
        label=_("Public chat room"),
        widget=forms.TextInput(),
        help_text=MATRIX_ROOM_REFERENCE_HELP,
    )
    room_private_visibility = forms.BooleanField(
        label=_("Show links to the private chat room"),
        required=False,
    )
    room_private_matrix_reference = forms.RegexField(
        MATRIX_ROOM_REFERENCE_REGEX,
        required=True,
        strip=True,
        label=_("Private chat room"),
        widget=forms.TextInput(),
        help_text=MATRIX_ROOM_REFERENCE_HELP,
    )
