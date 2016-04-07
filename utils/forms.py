from crispy_forms import helper, layout
from django import forms

class LayoutMixin:
    def get_helper(self):
        h = helper.FormHelper()
        h.layout = layout.Layout(*self.get_layout())
        return h

    def get_layout(self):
        layout = self.layout if hasattr(self, 'layout') else tuple()
        if not isinstance(layout, (tuple, list)):
            layout = (layout,)
        return layout
        
class FormMixin(LayoutMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.get_helper()

class ExtraFormMixin(FormMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs['instance'] = self.get_instance()
        self.extra_form = self.extra_form_class(*args, **kwargs)
        self.errors.update(self.extra_form.errors)
        self.fields.update(self.extra_form.fields)
        self.initial.update(self.extra_form.initial)

    def is_valid(self):
        return super().is_valid() and self.extra_form.is_valid()

    def save(self):
        self.extra_form.save()
        return super().save()

class Submit(layout.Submit):
    def __init__(self, value):
        super().__init__('submit', value)
