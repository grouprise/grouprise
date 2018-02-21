import django
from django import forms
from django.core.exceptions import ObjectDoesNotExist

from features.content import forms as content
from features.content.models import Content
from . import models


SimpleOptionFormSet = forms.modelformset_factory(
        models.SimpleOption, fields=('title',), labels={'title': 'Antwort'}, min_num=1,
        validate_min=True, can_delete=True)


EventOptionFormSet = forms.modelformset_factory(
        models.EventOption, fields=('time', 'until_time'),
        labels={'time': 'Datum / Zeit', 'until_time': 'Ende'},
        min_num=1, validate_min=True, can_delete=True)


class OptionMixin:
    def is_valid(self):
        return super().is_valid() and self.options.is_valid()

    def save_content_relations(self, commit):
        # FIXME: remove when django bug #28988 is fixed
        self.instance.container.poll = models.Poll.objects.create()
        self.instance.container.save()

        for form in self.options.forms:
            form.instance.poll = self.instance.container.poll
        self.options.save(commit)


class Create(OptionMixin, content.Create):
    # FIXME: replace by models.Poll when django bug #28988 is fixed
    container_class = Content

    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))
    poll_type = forms.ChoiceField(
            label='Art der Antwortmöglichkeiten',
            choices=[('simple', 'einfacher Text'), ('event', 'Datum / Zeit')],
            initial='simple', widget=forms.Select({'data-poll-type': ''}))
    vote_type = forms.ChoiceField(
            label='Art der Abstimmmöglichkeiten',
            choices=[('simple', 'Ja/Nein/Vielleicht'),
                     ('condorcet', 'Stimmen ordnen (rangbasiert)')],
            initial='simple', widget=forms.Select({'data-poll-vote-type': ''}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_type_change = self.data.get('change_type')

        # init options
        if self.data.get('poll_type') == 'event':
            self.options = EventOptionFormSet(
                    data=kwargs.get('data'), queryset=models.EventOption.objects.none())
        else:
            self.options = SimpleOptionFormSet(
                    data=kwargs.get('data'), queryset=models.SimpleOption.objects.none())
        self.options.extra = 0

        # permit empty form in case of type change
        if self.is_type_change:
            self.empty_permitted = True
            for form in self.options.forms:
                form.empty_permitted = True

    def is_valid(self):
        # prevent saving in case of type change
        return False if self.is_type_change else super().is_valid()

    def save(self, commit=True):
        association = super().save(commit)
        association.container.poll.condorcet = self.cleaned_data['vote_type'] == 'condorcet'
        association.container.poll.save()
        if commit:
            self.send_post_create()
        return association


class Update(OptionMixin, content.Update):
    text = forms.CharField(label='Beschreibung / Frage', widget=forms.Textarea({'rows': 2}))
    poll_type = forms.CharField(widget=forms.HiddenInput({'data-poll-type': ''}))
    poll_type = forms.CharField(widget=forms.HiddenInput({'data-poll-type': ''}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            models.Option.objects.filter(poll=self.instance.container).first().eventoption
            self.options = EventOptionFormSet(
                    data=kwargs.get('data'),
                    queryset=models.EventOption.objects.filter(poll=self.instance.container))
            self.fields['poll_type'].initial = 'event'
        except ObjectDoesNotExist:
            self.options = SimpleOptionFormSet(
                    data=kwargs.get('data'),
                    queryset=models.SimpleOption.objects.filter(poll=self.instance.container))
            self.fields['poll_type'].initial = 'simple'
        self.options.extra = 0

    def get_initial_for_field(self, field, field_name):
        if field_name == 'poll_type':
            return {
                EventOptionFormSet: 'event',
                SimpleOptionFormSet: 'simple'
            }[type(self.options)]
        else:
            return super().get_initial_for_field(field, field_name)


SimpleVoteFormSet = forms.modelformset_factory(
        models.SimpleVote, fields=('endorse',), labels={'endorse': 'Zustimmung'},
        widgets={'endorse': forms.RadioSelect(
            choices=[(True, 'Ja'), (False, 'Nein'), (None, 'Vielleicht')])})


CondorcetVoteFormSet = forms.modelformset_factory(
        models.CondorcetVote, fields=('rank',), labels={'rank': 'Rang / Platz'})


class Vote(forms.ModelForm):
    class Meta:
        model = models.SimpleVote
        fields = ('anonymous',)
        labels = {'anonymous': 'Name/Alias'}

    def __init__(self, poll, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.voter and self.instance.voter.user.is_authenticated:
            del self.fields['anonymous']
        else:
            self.fields['anonymous'].required = True

        self.poll = poll
        options = poll.options.all()
        if self.poll.condorcet:
            self.votes = CondorcetVoteFormSet(
                    data=kwargs.get('data'), queryset=models.SimpleVote.objects.none())
        else:
            self.votes = SimpleVoteFormSet(
                    data=kwargs.get('data'), queryset=models.SimpleVote.objects.none())
        self.votes.extra = len(options)
        for i, form in enumerate(self.votes.forms):
            form.instance.option = options[i]

    def clean_anonymous(self):
        anon = self.cleaned_data['anonymous']
        if models.SimpleVote.objects.filter(option__poll=self.poll, anonymous=anon).exists():
            raise django.forms.ValidationError('%s hat bereits abgestimmt.' % anon)
        return anon

    def is_valid(self):
        return super().is_valid() and self.votes.is_valid()

    def save(self, commit=True):
        vote = super().save(False)
        for form in self.votes.forms:
            form.instance.anonymous = self.instance.anonymous
            form.instance.voter = self.instance.voter
            form.save(commit)
        return vote
