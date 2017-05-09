from django import forms

from features.content import forms as content
from . import models


OptionFormSet = forms.modelformset_factory(
        models.Option, fields=('title',), labels={'title': 'Antwort'}, min_num=1,
        validate_min=True, can_delete=True)


class OptionMixin:
    def is_valid(self):
        return super().is_valid() and self.options.is_valid()

    def save(self, commit=True):
        association = super().save(commit)
        for form in self.options.forms:
            form.instance.poll = association.container
        self.options.save(commit)
        return association


class Create(OptionMixin, content.Create):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = OptionFormSet(
                data=kwargs.get('data'), queryset=models.Option.objects.none())
        self.options.extra = 4


class Update(OptionMixin, content.Update):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options = OptionFormSet(
                data=kwargs.get('data'),
                queryset=models.Option.objects.filter(poll=self.instance.container))
        self.options.extra = 2


VoteFormSet = forms.modelformset_factory(
        models.Vote, fields=('endorse',), labels={'endorse': 'Ja'})


class Vote(forms.ModelForm):
    class Meta:
        model = models.Vote
        fields = []

    def __init__(self, *args, options=None, **kwargs):
        self.options = options
        super().__init__(*args, **kwargs)
        self.votes = VoteFormSet(data=kwargs.get('data'), queryset=models.Vote.objects.none())
        self.votes.extra = 3

    def is_valid(self):
        return super().is_valid() and self.votes.is_valid()

    def save(self, commit=True):
        vote = super().save(False)
        for i, form in enumerate(self.votes.forms):
            form.instance.option = self.options[i]
            form.instance.voter = vote.voter
            form.save(commit)
        return vote
