import random
from typing import Tuple

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .utils import hash_captcha_answer


class EditorTextarea(forms.Textarea):
    has_buttons = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"]["editor"] = True
        return context


class GroupSelect(forms.Select):
    template_name = "core/widgets/group_select.html"


class CaptchaWidget(forms.MultiWidget):
    template_name = "core/widgets/captcha.html"

    CAPTCHA_QUESTIONS = [
        (_("Which season follows after winter?"), {_("spring")}),
        (_("How many days does a week have?"), {"7", _("seven")}),
        (_("How many months does a year have?"), {"12", _("twelve")}),
        (_("Which day follows after Wednesday?"), {_("Thursday")}),
        (_("What is the color of snow?"), {_("white")}),
        (_("What is the opposite of 'day'?"), {_("night")}),
    ]

    def __init__(self):
        widgets = (
            # this is the answer input field
            forms.TextInput(attrs={"size": "5"}),
            # this is the hashed answer field to compare to
            forms.HiddenInput(),
        )
        super().__init__(widgets)

    def get_context(self, *args, **kwargs):
        ctx = super().get_context(*args, **kwargs)
        ctx["label_id"] = ctx["widget"]["subwidgets"][0]["attrs"]["id"]
        ctx["question_html"] = self.question_html
        return ctx

    def decompress(self, value):
        return [None, None]

    def render(self, name, value, **kwargs):
        # hash the answer and set the hidden value of form
        question_html, hashed_answer = self.get_captcha()
        value = ["", hashed_answer]
        self.question_html = question_html
        return super().render(name, value, **kwargs)

    @classmethod
    def get_captcha(cls) -> Tuple[str, str]:
        question, answers = random.choice(cls.CAPTCHA_QUESTIONS)
        hashed_answers = " ".join(
            hash_captcha_answer(answer) for answer in sorted(answers)
        )
        return question, hashed_answers


class CaptchaField(forms.MultiValueField):
    default_error_messages = {
        "invalid": _("The answer was not quite correct. Please try it again!"),
    }

    def __init__(self, *args, **kwargs):
        widget = CaptchaWidget()
        kwargs["required"] = True
        kwargs.setdefault("widget", widget)
        super().__init__(
            [
                # the answer given by the user
                forms.CharField(
                    error_messages=self.default_error_messages,
                    localize=True,
                    required=False,
                ),
                # the expected hash for the answer
                forms.CharField(required=False),
            ],
            *args,
            **kwargs,
        )

    def get_bound_field(self, *args, **kwargs):
        """disable field label"""
        field = super().get_bound_field(*args, **kwargs)
        field.label = None
        return field

    def compress(self, data_list):
        """Compress takes the place of 'clean' with MultiValueFields"""
        if data_list:
            answer, expected_combined_hashed_answers = data_list
            expected_hashed_answers = expected_combined_hashed_answers.split()
            given_hashed_answer = hash_captcha_answer(answer)
            if given_hashed_answer not in expected_hashed_answers:
                raise ValidationError(self.error_messages["invalid"])
        return None
