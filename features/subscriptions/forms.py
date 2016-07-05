
class Attention(utils_forms.FormMixin, forms.ModelForm):
    attendee_email = forms.EmailField(disabled=True, widget=forms.HiddenInput)
    attended_object = forms.ModelChoiceField(disabled=True, queryset=content_models.Content.objects.all(), widget=forms.HiddenInput)
    layout = ('attendee_email', 
            layout.HTML('<p>Möchtest Du per E-Mail benachrichtigt werden, '
                'wenn dem Beitrag neue Kommentare hinzugefügt werden?</p>'),
            utils_forms.Submit('Benachrichtigungen erhalten'))

    class Meta:
        fields = ('attended_object',)
        model = subscriptions_models.Subscription

    def save(self):
        attention = super().save(commit=False)
        attention.attendee = models.Gestalt.objects.get(user__email=self.cleaned_data['attendee_email'])
        attention.attended_object = self.cleaned_data['attended_object']
        attention.save()
        return attention


class GroupAttention(utils_forms.FormMixin, forms.ModelForm):
    attendee_email = forms.EmailField(disabled=True, widget=forms.HiddenInput)
    group = forms.ModelChoiceField(disabled=True, queryset=models.Group.objects.all(), widget=forms.HiddenInput)
    layout = ('attendee_email', 
            layout.HTML('<p>Möchtest Du per E-Mail benachrichtigt werden, '
                'wenn Mitglieder der Gruppe <em>{{ group }}</em> neue Beiträge '
                'veröffentlichen?</p>'),
            utils_forms.Submit('Benachrichtigungen erhalten'))

    class Meta:
        fields = ('group',)
        model = subscriptions_models.Subscription

    def save(self):
        attention = super().save(commit=False)
        attention.attendee = models.Gestalt.objects.get(user__email=self.cleaned_data['attendee_email'])
        attention.save()
        return attention
