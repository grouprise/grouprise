from . import base
from .. import forms
from django.contrib.messages import views as messages_views
from django.forms import models as model_forms
from django.views.generic import base as django_base, edit as django_edit


class MessageMixin(messages_views.SuccessMessageMixin):
    def get_success_message(self, cleaned_data):
        return getattr(self, 'message', None)


class ModelFormMixin(django_edit.ModelFormMixin):
    def __init__(self, **kwargs):
        self.data_fields = [c(self) for c in self.data_field_classes]

    def get_form_class(self):
        return model_forms.modelform_factory(
                self.model,
                fields=self.get_model_form_fields(),
                form=forms.ModelForm)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['action'] = self.action
        kwargs['data_fields'] = self.data_fields
        kwargs['description'] = getattr(self, 'description', None)
        return kwargs

    def get_model_form_fields(self):
        fields = [f.get_model_form_field() for f in self.data_fields]
        return list(filter(None, fields))

    def get_success_url(self):
        return self.related_object.get_absolute_url()


class ProcessFormView(base.View):
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class BaseCreateView(MessageMixin, ModelFormMixin, ProcessFormView):
    def dispatch(self, *args, **kwargs):
        self.object = None
        self.related_object = self.get_related_object()
        return super().dispatch(*args, **kwargs)

    def get_menu(self):
        return type(self.related_object).__name__

    def get_parent(self):
        return self.related_object

    def get_permission_object(self):
        return self.related_object


class TemplateResponseMixin(django_base.TemplateResponseMixin):
    def get_template_names(self):
        return ['stadt/form.html']
