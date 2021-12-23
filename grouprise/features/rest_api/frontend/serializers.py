import django
from rest_framework import serializers
from taggit.models import Tag

from grouprise import core
from grouprise.features.gestalten.models import Gestalt, GestaltSetting
from grouprise.features.groups.models import Group
from grouprise.features.images.models import Image
from grouprise.features.polls.models import (
    Option,
    Vote,
    VoteType,
    WorkaroundPoll,
    resolve_vote,
)


def validate_file_size(image):
    try:
        core.models.validate_file_size(image["file"])
    except django.forms.ValidationError as e:
        raise serializers.ValidationError(e)


class IncludableFieldSerializerMixin:
    OPTIONAL_INCLUDABLE_FIELDS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            included_fields = [
                field
                for field in self.context["request"].GET.get("include", "").split(",")
                if field in self.OPTIONAL_INCLUDABLE_FIELDS
            ]
        except (AttributeError, KeyError):
            pass
        else:
            for field in set(self.OPTIONAL_INCLUDABLE_FIELDS) - set(included_fields):
                self.fields.pop(field)


class GestaltSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="__str__", read_only=True)
    initials = serializers.CharField(source="get_initials", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)

    class Meta:
        model = Gestalt
        fields = ("id", "name", "initials", "about", "avatar", "avatar_color", "url")


class GestaltOrAnonSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if "id" in data and data["id"] is not None:
            return Gestalt.objects.get(pk=data["id"])
        # todo validate name if no valid id was provided
        return data

    def run_validators(self, value):
        """the 'run_validators' method of serializers.Serializer seems to expect a dict"""
        if not isinstance(value, dict):
            value = {"id": value.id, "name": value.name}
        return super().run_validators(value)

    class Meta:
        fields = ("id", "name")


class GestaltSettingSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        gestalt = self.context["view"].request.user.gestalt
        fields["gestalt"].queryset = Gestalt.objects.filter(id=gestalt.id)
        return fields

    class Meta:
        model = GestaltSetting
        fields = ("id", "gestalt", "name", "category", "value")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name")


class GroupSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    initials = serializers.CharField(source="get_initials", read_only=True)
    url = serializers.CharField(source="get_absolute_url", read_only=True)
    cover = serializers.SerializerMethodField()

    def get_cover(self, obj: Group):
        return obj.get_cover_url()

    class Meta:
        model = Group
        fields = (
            "id",
            "slug",
            "name",
            "initials",
            "description",
            "avatar",
            "avatar_color",
            "tags",
            "cover",
            "url",
        )


class ImageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="file.name", read_only=True)
    path = serializers.CharField(source="file.url", read_only=True)

    class Meta:
        model = Image
        fields = ("id", "file", "title", "creator", "path")
        validators = [validate_file_size]

    def _get_gestalt(self):
        try:
            return self.context["request"].user.gestalt
        except AttributeError:
            return None

    def create(self, validated_data):
        validated_data.update({"creator": self._get_gestalt()})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data.update({"creator": self._get_gestalt()})
        return super().update(instance, validated_data)

    def to_representation(self, instance: Image):
        repr = super().to_representation(instance)
        repr["preview"] = instance.preview_api.url
        return repr


class OptionSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()

    def get_title(self, instance: Option):
        return str(instance)

    class Meta:
        model = Option
        fields = (
            "id",
            "title",
        )


class VoterSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        if type(instance) is str:
            return instance
        else:
            return GestaltSerializer().to_representation(instance)


class PollSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()
    last_voted = serializers.SerializerMethodField()

    def get_options(self, instance: WorkaroundPoll):
        options = sorted(list(instance.options.all()))
        return OptionSerializer(options, many=True).data

    def get_last_voted(self, instance: WorkaroundPoll):
        last_vote = (
            Vote.objects.filter(option__poll=instance).order_by("time_updated").last()
        )
        return last_vote.time_updated if last_vote else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        vote_data = resolve_vote(instance)
        voter_serializer = VoterSerializer()

        if instance.vote_type is VoteType.CONDORCET:
            representation.update(
                {
                    "options_winner": getattr(vote_data["winner"], "id", None),
                    "options_ranking": [option.id for option in vote_data["ranking"]],
                    "votes": [
                        dict(
                            voter=voter_serializer.to_representation(voter),
                            ranking=[
                                option.id
                                for option in sorted(
                                    options.keys(),
                                    key=lambda o: options[o],
                                    reverse=True,
                                )
                            ],
                        )
                        for voter, options in vote_data["votes"].items()
                    ],
                }
            )
        elif instance.vote_type is VoteType.SIMPLE:
            representation.update(
                {
                    "options_winner": getattr(vote_data["winner"], "id", None),
                    "options_ranking": [
                        option.id
                        for option, counts in sorted(
                            vote_data["vote_count"].items(),
                            key=lambda x: x[1].score,
                            reverse=True,
                        )
                    ],
                    "vote_counts": [
                        dict(
                            option=option.id,
                            score=counts.score,
                            counts=counts.serialize(),
                        )
                        for option, counts in vote_data["vote_count"].items()
                    ],
                    "votes": [
                        dict(
                            voter=voter_serializer.to_representation(voter),
                            endorsements=[
                                dict(
                                    option=option.id,
                                    endorsement=vote.simplevote.endorse,
                                )
                                for option, vote in votes.items()
                                if isinstance(option, Option)
                            ],
                        )
                        for voter, votes in vote_data["votes"].items()
                    ],
                }
            )

        return representation

    class Meta:
        model = WorkaroundPoll
        fields = (
            "id",
            "options",
            "last_voted",
        )


class EndorsementsSerializer(serializers.Serializer):
    option = serializers.PrimaryKeyRelatedField(queryset=Option.objects)
    endorsement = serializers.NullBooleanField()


class PollVoteSerializer(serializers.Serializer):
    gestalt = GestaltOrAnonSerializer()
    ranking = serializers.PrimaryKeyRelatedField(
        many=True, required=False, queryset=Option.objects
    )
    endorsements = EndorsementsSerializer(many=True, required=False)
