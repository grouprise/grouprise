import collections
import enum

from django.db import models
from django.utils import timezone
from py3votecore.schulze_method import SchulzeMethod

import core.models


class VoteType(enum.Enum):
    SIMPLE = 'simple'
    RANK = 'rank'


def _resolve_condorcet_vote(votes):
    def _resolve_pair_order(winner, strong_pairs):
        rankings = strong_pairs.copy()
        ordered_pairs = sorted(rankings.keys(), key=lambda pair: rankings[pair])
        result = []

        if winner is not None:
            result.append(winner)

        def _get_highest_ranking(option=None, ignore_options=None):
            ignore_options = ignore_options or []

            if not ordered_pairs:
                return None

            if option:
                for pair in ordered_pairs:
                    if pair[0] == option and pair[1] not in ignore_options:
                        return pair[1]
                return None
            else:
                return ordered_pairs[0][0]

        while True:
            try:
                last_option = result[-1]
            except IndexError:
                last_option = None
            next_option = _get_highest_ranking(last_option, result)
            if not next_option:
                break
            result.append(next_option)

        return result

    votes_dict = collections.defaultdict(dict)
    for vote in votes:
        if vote.voter:
            votes_dict[vote.voter][vote.option] = vote.condorcetvote.rank
        else:
            votes_dict[vote.anonymous][vote.option] = vote.condorcetvote.rank

    vote_data = [{'ballot': b} for b in votes_dict.values()]
    result = SchulzeMethod(vote_data).as_dict() if vote_data else {}
    winner = result.get('winner', None)

    data = {
        'votes': votes_dict,
        'winner': winner,
        'ranking': _resolve_pair_order(winner, result.get('strong_pairs', {}))
    }
    return data


def _resolve_simple_vote(votes):
    def get_winner(vote_count: dict):
        result = []
        for option, votes in vote_count.items():
            result.append(
                (option, votes['yes'] + votes['maybe'] * .33334)
            )
        try:
            return sorted(result, key=lambda item: item[1], reverse=True)[0][0]
        except IndexError:
            return None

    def vote_key(endorse):
        if endorse is None:
            return 'maybe'
        elif endorse:
            return 'yes'
        else:
            return 'no'

    votes_dict = collections.defaultdict(dict)
    vote_count = collections.defaultdict(lambda: dict(yes=0, no=0, maybe=0))
    for vote in votes:
        vote_count[vote.option][vote_key(vote.simplevote.endorse)] += 1
        if vote.voter:
            votes_dict[vote.voter][vote.option] = vote
            votes_dict[vote.voter]['latest'] = vote
        else:
            votes_dict[vote.anonymous][vote.option] = vote
            votes_dict[vote.anonymous]['latest'] = vote
    return {
        'votes': votes_dict,
        'vote_count': vote_count,
        'winner': get_winner(vote_count)
    }


def resolve_voters(poll):
    _votes = Vote.objects.filter(option__poll=poll).all()

    voters = []
    for vote in _votes:
        if vote.voter and vote.voter not in voters:
            voters.append(vote.voter)
        elif vote.anonymous and vote.anonymous not in voters:
            voters.append(vote.anonymous)
    return voters


def resolve_vote(poll):
    _votes = Vote.objects.filter(option__poll=poll).all()

    if poll.condorcet:
        votes = _resolve_condorcet_vote(_votes)
    else:
        votes = _resolve_simple_vote(_votes)

    return votes


# FIXME: inherit from content.Content when django bug #28988 is fixed
class Poll(core.models.Model):
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
