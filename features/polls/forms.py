import django
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
        fields = ('anonymous',)
        labels = {'anonymous': 'Name/Alias'}

    def __init__(self, poll, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.voter and self.instance.voter.user.is_authenticated():
            del self.fields['anonymous']
        else:
            self.fields['anonymous'].required = True
        # self.fields['anonymous'].help_text = django.utils.safestring.mark_safe(
        #        '<a href="{}?next=">Anmelden</a> oder Name/Alias angeben'.format(
        #            django.core.urlresolvers.reverse('account_login')))

        options = poll.options.all()
        self.votes = VoteFormSet(data=kwargs.get('data'), queryset=models.Vote.objects.none())
        self.votes.extra = len(options)
        for i, form in enumerate(self.votes.forms):
            form.instance.option = options[i]

    def is_valid(self):
        return super().is_valid() and self.votes.is_valid()

    def save(self, commit=True):
        vote = super().save(False)
        for form in self.votes.forms:
            form.instance.anonymous = self.instance.anonymous
            form.instance.voter = self.instance.voter
            form.save(commit)
        return vote
