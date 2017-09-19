from django import forms

from features.gestalten.forms import GestaltByEmailField
from features.subscriptions.models import Subscription


class Subscribe(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ('subscriber',)
        field_classes = {'subscriber': GestaltByEmailField}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'subscriber'):
            del self.fields['subscriber']
