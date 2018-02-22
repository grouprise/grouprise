import collections
import copy
import enum
import subprocess

from django.db import models
from django.utils import timezone
from py3votecore.schulze_method import SchulzeMethod
from py3votecore.tie_breaker import TieBreaker

import core.models


class VoteType(enum.Enum):
    SIMPLE = 'simple'
    RANK = 'rank'

    def __str__(self):
        return str(self.value)


def _graph_to_svg(graph, winner, tied_winners=None):
    """ convert a graph (see pygraph.classes.digraph) to an SVG visualization

    This operation requires the external "dot" executable (package "graphviz").
    The winner and (optional) candidates that reached a tie with the winner are marked with
    separate colors.
    """
    # TODO: move this late import to the top of the module, if we want to use this feature
    import pygraph.readwrite.dot
    # The color can be given as "#RGBA" or by name.
    fill_colors = {"winner": "#C00000C0",
                   "tied_winners": "#00C000C0",
                   "others": "#0000C0C0"}
    # add background colors to all nodes
    for node_name in graph.nodes():
        graph.add_node_attribute(node_name, ("style", "filled"))
        if node_name == winner:
            color = fill_colors["winner"]
        elif tied_winners and (node_name in tied_winners):
            color = fill_colors["tied_winners"]
        else:
            color = fill_colors["others"]
        graph.add_node_attribute(node_name, ("fillcolor", color))
    dot_graph = pygraph.readwrite.dot.write(graph, weighted=True)
    proc = subprocess.Popen(["dot", "-Tsvg"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate(dot_graph.encode("utf-8"))
    return stdout.decode("utf-8")


def _resolve_condorcet_vote(options, votes):
    def get_ranked_winners(vote_data, tie_breaker, excluded_candidate=None):
        """ recursively calculate subsequent winners by taking out the current winner in each round

        BEWARE: the only goal of rank-based vote resolution is the calculation of a fair winner.
        This method is not usable for creating a linear ranking (the input data is too complex for
        that). The result of the calculation below is deterministic, but it is not fair.
        The weighted graph is probably a much better (non-linear) visualization of the result.
        """
        if vote_data:
            # remove excluded candiate from voting data
            reduced_votes = []
            for ballot in vote_data:
                ballot = copy.deepcopy(ballot)
                ballot['ballot'].pop(excluded_candidate, None)
                # only add non-empty ballots
                if ballot['ballot']:
                    reduced_votes.append(ballot)
            if reduced_votes:
                winner = SchulzeMethod(reduced_votes, tie_breaker=tie_breaker).winner
                if winner is not None:
                    yield winner
                    yield from get_ranked_winners(reduced_votes, tie_breaker,
                                                  excluded_candidate=winner)

    votes_dict = collections.defaultdict(dict)
    for vote in votes:
        if vote.voter:
            votes_dict[vote.voter][vote.option] = vote.condorcetvote.rank
        else:
            votes_dict[vote.anonymous][vote.option] = vote.condorcetvote.rank

    vote_data = [{'ballot': b} for b in votes_dict.values()]
    tie_breaker = TieBreaker(list(options))
    if vote_data:
        result = SchulzeMethod(vote_data, tie_breaker=tie_breaker)
        result_dict = result.as_dict()
        winner = result_dict.get('winner', None)
        # "tied_winners": all candidates that reached a tie with the winner (including the winner).
        # This attribute is undefined if no one tied with the winner.
        # This tie is just a "technical tie" of the Condorcet Method: it does not mean, that the
        # tied candidates are equally suitable for being a winner.
        # E.g. for [("C", "A", "B"), ("A", "B", "C")] the winner is "A" (winning against B and tied
        # with C). "C" is tied with the winner, but it did not win against "B" - thus it is less
        # eligible for winning.
        tied_winners = result_dict.get('tied_winners', [])
        ranking = [winner]
        ranking.extend(get_ranked_winners(vote_data, tie_breaker, excluded_candidate=winner))
        graph_svg = _graph_to_svg(result.graph, winner, tied_winners)
    else:
        winner = None
        ranking = []
        graph_svg = None

    data = {
        'votes': votes_dict,
        'winner': winner,
        'ranking': ranking,
        'graph_svg': graph_svg,
    }
    return data


def _resolve_simple_vote(votes):
    class VoteCount:
        def __init__(self) -> None:
            self.yes = 0
            self.no = 0
            self.maybe = 0

        def __add__(self, endorse):
            if endorse is None:
                self.maybe += 1
            elif endorse:
                self.yes += 1
            else:
                self.no += 1
            return self

        @property
        def score(self):
            return self.yes + self.maybe * .33334

        def serialize(self):
            return {key: getattr(self, key) for key in ['yes', 'no', 'maybe']}

    def get_winner(vote_count: dict):
        result = []
        for option, votes in vote_count.items():
            result.append(
                (option, votes.score)
            )
        try:
            return sorted(result, key=lambda item: item[1], reverse=True)[0][0]
        except IndexError:
            return None

    votes_dict = collections.defaultdict(dict)
    vote_count = collections.defaultdict(lambda: VoteCount())
    for vote in votes:
        vote_count[vote.option] += vote.simplevote.endorse
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
        votes = _resolve_condorcet_vote(poll.options.all(), _votes)
    else:
        votes = _resolve_simple_vote(_votes)

    return votes


# FIXME: inherit from content.Content when django bug #28988 is fixed
class WorkaroundPoll(core.models.Model):
    condorcet = models.BooleanField(default=False)

    @property
    def vote_type(self):
        return VoteType.RANK if self.condorcet else VoteType.SIMPLE


class Option(core.models.Model):
    poll = models.ForeignKey(
            'WorkaroundPoll', related_name='options', on_delete=models.CASCADE, null=True)

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
