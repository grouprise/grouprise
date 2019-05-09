from django import forms


class EditorTextarea(forms.Textarea):
    has_buttons = True

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['editor'] = True
        return context


class GroupSelect(forms.Select):
    template_name = 'core/widgets/group_select.html'
