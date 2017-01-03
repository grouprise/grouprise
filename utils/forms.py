"""
This file is part of stadtgestalten.

stadtgestalten is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

stadtgestalten is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero Public License for more details.

You should have received a copy of the GNU Affero Public License
along with stadtgestalten.  If not, see <http://www.gnu.org/licenses/>.
"""

from crispy_forms import helper, layout, bootstrap


class LayoutMixin:
    def get_helper(self):
        h = helper.FormHelper()
        h.layout = layout.Layout(*self.get_layout())
        if hasattr(self, 'inline') and self.inline:
            h.field_template = 'bootstrap3/layout/inline_field.html'
            h.form_class = 'form-inline'
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


class EditorField(layout.Field):
    def __init__(self, *args, **kwargs):
        kwargs['data_component'] = 'editor'
        super().__init__(*args, **kwargs)


class Field(layout.Field):
    def __init__(self, name, **kwargs):
        self.constant = False
        if 'type' in kwargs and kwargs['type'] == 'constant':
            self.constant = True
            kwargs['type'] = 'hidden'
        super().__init__(name, **kwargs)


class Submit(bootstrap.StrictButton):
    field_classes = "btn btn-primary"

    def __init__(self, content, name='', field_classes=None, value="submit"):
        if field_classes is not None:
            self.field_classes = field_classes
        super().__init__(content, name=name, value=value, type="submit")
