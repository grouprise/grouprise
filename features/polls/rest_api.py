from contextlib import contextmanager
from django.http import Http404
from django.core.exceptions import PermissionDenied
from rest_framework import viewsets, mixins, serializers, permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from core import api
from features.gestalten.rest_api import GestaltSerializer, GestaltOrAnonSerializer
from . import models


class OptionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, instance: models.Option):
        return str(instance)

    class Meta:
        model = models.Option
        fields = ('id', 'title',)


class VoteSerializer(serializers.ModelSerializer):
    option = serializers.PrimaryKeyRelatedField(read_only=True)
    voter = serializers.SerializerMethodField()

    def get_voter(self, vote: models.Vote):
        if vote.voter:
            return GestaltSerializer(data=vote.voter)
        elif vote.anonymous:
            return vote.anonymous
        else:
            return None

    class Meta:
        model = models.Vote
        fields = ('id', 'option', 'voter',)


class VoterSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if type(instance) is str:
            return instance
        else:
            return GestaltSerializer().to_representation(instance)


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    def to_representation(self, instance):
        vote_data = models.resolve_vote(instance)
        representation = super().to_representation(instance)
        voter_serializer = VoterSerializer()

        if 'ranking' in vote_data:
            representation.update({
                'options_winner': getattr(vote_data['winner'], 'id', None),
                'options_ranking': [option.id for option in vote_data['ranking']],
                'votes': [
                    dict(
                        voter=voter_serializer.to_representation(voter),
                        ranking=[
                            option.id for option in sorted(options.keys(),
                                                           key=lambda o: options[o], reverse=True)
                        ]
                    ) for voter, options in vote_data['votes'].items()
                ]
            })
        else:
            representation.update({
                'options_winner': getattr(vote_data['winner'], 'id', None),
                'options_ranking': [
                    option.id for option, counts in
                    sorted(vote_data['vote_count'].items(),
                           key=lambda x: x[1].score, reverse=True)
                ],
                'vote_counts': [
                    dict(option=option.id, score=counts.score, counts=counts.serialize())
                    for option, counts in vote_data['vote_count'].items()
                ],
                'votes': [
                    dict(
                        voter=voter_serializer.to_representation(voter),
                        endorsements=[
                            dict(option=option.id, endorsement=vote.simplevote.endorse)
                            for option, vote in votes.items()
                            if isinstance(option, models.Option)
                        ]
                    ) for voter, votes in vote_data['votes'].items()
                ]
            })

        return representation

    class Meta:
        model = models.WorkaroundPoll
        fields = ('id', 'options',)


class EndorsementsSerializer(serializers.Serializer):
    option = serializers.PrimaryKeyRelatedField(queryset=models.Option.objects)
    endorsement = serializers.NullBooleanField()


class PollVoteSerializer(serializers.Serializer):
    gestalt = GestaltOrAnonSerializer()
    ranking = serializers.PrimaryKeyRelatedField(many=True, required=False,
                                                 queryset=models.Option.objects)
    endorsements = EndorsementsSerializer(many=True, required=False)


@api_view(('POST',))
@permission_classes((permissions.AllowAny,))
def vote(request, pk):
    try:
        poll = models.WorkaroundPoll.objects.get(pk=pk)
    except models.WorkaroundPoll.DoesNotExist:
        raise Http404()

    payload = PollVoteSerializer().to_internal_value(request.data)

    can_vote = request.user.has_perm('polls.vote', poll.content.associations.first())
    can_anon_vote = not request.user.is_anonymous or models.Vote.objects \
        .filter(option__in=poll.options.all(), anonymous=payload['gestalt']['name']) \
        .count() == 0

    if not (can_vote and can_anon_vote):
        if can_anon_vote:
            raise PermissionDenied('VOTE_ERR_ANON_VOTED')
        else:
            raise PermissionDenied('VOTE_ERR_GESTALT_VOTED')

    @contextmanager
    def create_vote(base_model, option: models.Option):
        new_vote = base_model()  # type: models.Vote
        new_vote.option = option
        try:
            new_vote.voter = request.user.gestalt
        except AttributeError:
            new_vote.anonymous = payload['gestalt']['name']
        yield new_vote
        new_vote.save()

    if poll.vote_type is models.VoteType.CONDORCET:
        num_options = len(payload['ranking'])
        for (ranking, option) in enumerate(payload['ranking']):
            with create_vote(models.CondorcetVote, option) as condorcet_vote:
                condorcet_vote.rank = num_options - ranking
    elif poll.vote_type is models.VoteType.SIMPLE:
        for vote in payload['endorsements']:
            with create_vote(models.SimpleVote, vote['option']) as simple_vote:
                simple_vote.endorse = vote['endorsement']

    return Response(status=200)


@permission_classes((permissions.AllowAny,))
class PollSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PollSerializer
    filter_fields = ('id',)
    queryset = models.WorkaroundPoll.objects.all()


@api.register
def load(router):
    router.register(r'polls', PollSet, 'polls')
