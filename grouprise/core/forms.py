from django import forms
from simplemathcaptcha.fields import MathCaptchaField, MathCaptchaWidget


class EditorTextarea(forms.Textarea):
    has_buttons = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['editor'] = True
        return context


class GroupSelect(forms.Select):
    template_name = 'core/widgets/group_select.html'


class Captcha(MathCaptchaField):
    class Widget(MathCaptchaWidget):
        def get_context(self, *args, **kwargs):
            ctx = super().get_context(*args, **kwargs)
            ctx['label_id'] = ctx['widget']['subwidgets'][0]['attrs']['id']
            return ctx

    default_error_messages = {
        'invalid': 'Knapp daneben! Probiere es noch einmal!',
        'invalid_number': 'Bitte gib nur einfache Ziffern ein.',
    }

    def __init__(self, *args, **kwargs):
        widget = self.Widget(question_tmpl='Was ergibt %(num1)i %(operator)s %(num2)i?')
        kwargs.setdefault('widget', widget)
        super().__init__(*args, **kwargs)

    def get_bound_field(self, *args, **kwargs):
        field = super().get_bound_field(*args, **kwargs)
        field.label = None
        return field
