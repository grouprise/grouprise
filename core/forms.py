from crispy_forms import bootstrap, helper, layout
from django import forms


class EditorTextarea(forms.Textarea):
    has_buttons = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['editor'] = True
        return context


class GroupSelect(forms.Select):
    template_name = 'core/widgets/group_select.html'


class Submit(bootstrap.StrictButton):
    field_classes = "btn btn-primary"

    def __init__(self, value, name='', field_classes=None):
        if field_classes is not None:
            self.field_classes = field_classes
        super().__init__(value, name=name, value=value, type="submit")


class LayoutMixin:
    def get_helper(self):
        h = helper.FormHelper()
        h.layout = layout.Layout(*self.get_layout())
        if hasattr(self, 'inline') and self.inline:
            h.field_template = 'bootstrap3/layout/inline_field.html'
            h.form_class = 'form-inline'
        if hasattr(self, 'search') and self.search:
            h.field_template = 'bootstrap3/layout/inline_field.html'
            h.form_class = 'form-search'
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
        if hasattr(self, 'method'):
            self.helper.form_method = self.method
