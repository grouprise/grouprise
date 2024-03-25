from contextlib import contextmanager

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.response import Response

from grouprise.core.templatetags.defaulttags import markdown
from grouprise.features.associations.models import Association
from grouprise.features.content.models import Content
from grouprise.features.galleries.models import GalleryImage
from grouprise.features.gestalten.models import Gestalt, GestaltSetting
from grouprise.features.groups.models import Group
from grouprise.features.images.models import Image
from grouprise.features.memberships.models import Membership
from grouprise.features.polls.models import (
    CondorcetVote,
    Option,
    SimpleVote,
    Vote,
    VoteType,
    WorkaroundPoll,
)

from .filters import GroupFilter, ImageFilter
from .serializers import (
    GestaltSerializer,
    GestaltSettingSerializer,
    GroupSerializer,
    ImageSerializer,
    PollSerializer,
    PollVoteSerializer,
)

_PRESETS = {
    "content": {
        "heading_baselevel": 2,
    },
}


def permission(path):
    class UserPermission(permissions.BasePermission):
        def has_permission(self, request, view):
            gestalt_id = request.resolver_match.kwargs.get("gestalt")
            return request.user.gestalt.id == int(gestalt_id)

        def has_object_permission(self, request, view, obj):
            return request.user.gestalt == path(obj)

    return UserPermission


class GestaltSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GestaltSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Gestalt.objects.filter(pk=user.gestalt.pk)


class GestaltSettingSet(viewsets.ModelViewSet):
    serializer_class = GestaltSettingSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permission(lambda setting: setting.gestalt),
    )

    def get_queryset(self):
        return GestaltSetting.objects.filter(gestalt=self.kwargs["gestalt"])


@permission_classes((permissions.AllowAny,))
class GroupSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GroupSerializer
    filter_fields = (
        "id",
        "name",
        "slug",
    )
    filterset_class = GroupFilter
    queryset = Group.objects.all()


class ImageSet(
    mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet
):
    serializer_class = ImageSerializer
    filter_fields = ("id", "creator")
    filterset_class = ImageFilter

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Image.objects.none()

        # we want users to have access to
        # * images that they created themselves
        # * images part of a group gallery with user having membership in group
        # * images posted in a group as preview image with user having membership in group
        memberships = Membership.objects.filter(member=user.gestalt)
        groups = Group.objects.filter(memberships__in=memberships)
        associations = Association.objects.filter(
            container_type=ContentType.objects.get_for_model(Content),
            entity_type=ContentType.objects.get_for_model(Group),
            entity_id__in=groups,
        )
        group_content = Content.objects.filter(associations__in=associations)
        gallery_images = GalleryImage.objects.filter(
            gallery__in=group_content.filter(gallery_images__isnull=False)
        )
        gallery_image_ids = gallery_images.values_list("image", flat=True)
        preview_images = group_content.filter(image__isnull=False)
        preview_image_ids = preview_images.values_list("image", flat=True)

        return Image.objects.filter(
            Q(creator__user=user)  # own images
            | Q(id__in=gallery_image_ids)  # gallery images
            | Q(id__in=preview_image_ids)  # content preview images
        )

    def has_permission(self):
        if self.request.user.is_authenticated:
            if self.action == "create":
                return True
            elif self.action == "list":
                return True
            elif self.action == "retrieve":
                image = self.get_object()
                return self.request.user.has_perm("images.view", image)
            elif self.action == "update":
                image = self.get_object()
                return image.creator == self.request.user
        return False


class MarkdownView(viewsets.ViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        preset = _PRESETS[request.data.get("preset", "content")]
        text = request.data.get("content")
        return Response({"content": str(markdown(text, **preset))})


@permission_classes((permissions.AllowAny,))
class PollSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PollSerializer
    filter_fields = ("id",)
    queryset = WorkaroundPoll.objects.all()

    @action(["POST"], detail=True, permission_classes=[permissions.AllowAny])
    def vote(self, request, pk):
        poll = self.get_object()
        payload = PollVoteSerializer().to_internal_value(request.data)

        can_vote = request.user.has_perm(
            "polls.vote", poll.content.associations.first()
        )
        can_anon_vote = (
            not request.user.is_anonymous
            or Vote.objects.filter(
                option__in=poll.options.all(), anonymous=payload["gestalt"]["name"]
            ).count()
            == 0
        )

        if not (can_vote and can_anon_vote):
            if can_anon_vote:
                raise PermissionDenied("VOTE_ERR_ANON_VOTED")
            else:
                raise PermissionDenied("VOTE_ERR_GESTALT_VOTED")

        @contextmanager
        def create_vote(base_model, option: Option):
            new_vote = base_model()  # type: Vote
            new_vote.option = option
            try:
                new_vote.voter = request.user.gestalt
            except AttributeError:
                new_vote.anonymous = payload["gestalt"]["name"]
            yield new_vote
            new_vote.save()

        if poll.vote_type is VoteType.CONDORCET:
            num_options = len(payload["ranking"])
            for (ranking, option) in enumerate(payload["ranking"]):
                with create_vote(CondorcetVote, option) as condorcet_vote:
                    condorcet_vote.rank = num_options - ranking
        elif poll.vote_type is VoteType.SIMPLE:
            for vote in payload["endorsements"]:
                with create_vote(SimpleVote, vote["option"]) as simple_vote:
                    simple_vote.endorse = vote["endorsement"]

        return Response(status=200)
