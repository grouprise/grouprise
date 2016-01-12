from crispy_forms import helper, layout

class LayoutMixin(object):
    def get_form(self):
        form = super().get_form()
        form.helper = helper.FormHelper()
        form.helper.layout = layout.Layout(*self.get_layout())
        return form

    def get_layout(self):
        return self.layout
