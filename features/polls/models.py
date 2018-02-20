import enum

from django.db import models
from django.utils import timezone

import core.models
from features.content.models import Content


class VoteType(enum.Enum):
    SIMPLE = 'simple'
    RANK = 'rank'


class Poll(Content):
    condorcet = models.BooleanField(default=False)

    @property
    def vote_type(self):
        return VoteType.RANK if self.condorcet else VoteType.SIMPLE


class Option(core.models.Model):
    poll = models.ForeignKey(
            'Poll', related_name='options', on_delete=models.CASCADE, null=True)

    def __str__(self):
        if hasattr(self, 'simpleoption'):
            return self.simpleoption.__str__()
        elif hasattr(self, 'eventoption'):
            return self.eventoption.__str__()
        return super().__str__()

    # todo le, gt, and lt were necessary for evaluation with vote-core but seem wrong
    def __le__(self, other):
        return False

    def __gt__(self, other):
        return False

    def __lt__(self, other):
        return False

    class Meta:
        ordering = ('id', )


class SimpleOption(Option):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class EventOption(Option):
    time = models.DateTimeField()
    until_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        time = timezone.localtime(self.time)
        until_time = timezone.localtime(self.until_time) if self.until_time else None
        if time and until_time is None:
            return time.strftime('%d. %m.\n%H:%M')
        if time.date() == until_time.date():
            return '{date}\n{time_start} bis {time_end}'.format(
                date=time.strftime('%d. %m.'),
                time_start=time.strftime('%H:%M'),
                time_end=until_time.strftime('%H:%M'),
            )
        else:
            return '{time_start} bis\n{time_end}'.format(
                time_start=time.strftime('%d. %m. %H:%M'),
                time_end=until_time.strftime('%d. %m. %H:%M'),
            )


class Vote(core.models.Model):
    option = models.ForeignKey('Option', on_delete=models.CASCADE)
    voter = models.ForeignKey(
            'gestalten.Gestalt', null=True, related_name='votes', on_delete=models.PROTECT)
    anonymous = models.CharField(max_length=63, blank=True, null=True)
    time_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('option', 'voter'), ('option', 'anonymous'))
        ordering = ('time_updated', )


class SimpleVote(Vote):
    endorse = models.NullBooleanField(default=False)


class CondorcetVote(Vote):
    # higher rank == higher priority
    rank = models.SmallIntegerField()
