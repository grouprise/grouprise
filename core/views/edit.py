from . import base
from .. import forms
from django.contrib.messages import views as messages_views
from django.forms import models as model_forms
from django.views.generic import (
        base as django_base, detail as django_detail, edit as django_edit)


class MessageMixin(messages_views.SuccessMessageMixin):
    def get_success_message(self, cleaned_data):
        return getattr(self, 'message', None)


class TemplateResponseMixin(django_base.TemplateResponseMixin):
    def get_template_names(self):
        return ['stadt/form.html']


class FormMixin(MessageMixin, django_edit.FormMixin):
    def __init__(self, **kwargs):
        self.data_fields = [c(self) for c in self.data_field_classes]

    def get_form_class(self):
        return forms.Form

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.action
        kwargs['data_fields'] = self.data_fields
        kwargs['description'] = getattr(self, 'description', None)
        return kwargs

    def get_success_url(self):
        return self.related_object.get_absolute_url()


class ModelFormMixin(FormMixin, django_detail.SingleObjectMixin):
    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_form_class(self):
        return model_forms.modelform_factory(
                self.model,
                fields=self.get_model_form_fields(),
                form=forms.ModelForm)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        return kwargs

    def get_model_form_fields(self):
        fields = [f.get_model_form_field() for f in self.data_fields]
        return list(filter(None, fields))


class ProcessFormView(base.View):
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BaseFormView(FormMixin, ProcessFormView):
    pass


class FormView(TemplateResponseMixin, BaseFormView):
    pass


class BaseCreateView(ModelFormMixin, ProcessFormView):
    pass


class CreateView(TemplateResponseMixin, BaseCreateView):
    pass
