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

class Submit(layout.Submit):
    def __init__(self, value):
        super().__init__('submit', value)
