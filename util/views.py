from crispy_forms import helper, layout


class LayoutMixin(object):
    def get_form(self):
        form = super().get_form()
        form.helper = helper.FormHelper()
        form.helper.layout = layout.Layout(*self.get_layout())
        return form

    def get_layout(self):
        return self.layout


class NavigationMixin(object):
    def get_back_url(self):
        return self.get_success_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['back_url'] = self.get_back_url()
        return context
