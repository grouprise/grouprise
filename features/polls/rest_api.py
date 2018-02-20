from contextlib import contextmanager
from django.http import Http404
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
        fields = ('id', 'title', )


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
        fields = ('id', 'option', 'voter', )


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

        if 'ranking' in vote_data:
            voter_serializer = VoterSerializer()
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

        return representation

    class Meta:
        model = models.Poll
        fields = ('id', 'options', )


class PollVoteSerializer(serializers.Serializer):
    gestalt = GestaltOrAnonSerializer()
    ranking = serializers.PrimaryKeyRelatedField(many=True, required=False,
                                                 queryset=models.Option.objects)


# todo check user permissions
# todo check if user is allowed to vote
@api_view(('POST', ))
@permission_classes((permissions.AllowAny, ))
def vote(request, pk):
    try:
        poll = models.Poll.objects.get(pk=pk)
    except models.Poll.DoesNotExist:
        raise Http404()

    payload = PollVoteSerializer().to_internal_value(request.data)

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

    if poll.vote_type is models.VoteType.RANK:
        num_options = len(payload['ranking'])
        for (ranking, option) in enumerate(payload['ranking']):
            with create_vote(models.CondorcetVote, option) as condorcet_vote:
                condorcet_vote.rank = num_options - ranking
    elif poll.vote_type is models.VoteType.SIMPLE:
        # todo implement simple votes
        pass

    return Response(status=200)


# todo check user permissions
@permission_classes((permissions.AllowAny, ))
class PollSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PollSerializer
    filter_fields = ('id', )
    queryset = models.Poll.objects.all()


@api.register
def load(router):
    router.register(r'polls', PollSet, 'polls')
