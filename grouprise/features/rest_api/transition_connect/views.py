from rest_framework import viewsets, permissions
from rest_framework.decorators import permission_classes

from grouprise.features.associations.models import Association
from grouprise.features.groups.models import Group
from .serializers import EventListSerializer, EventRetrieveSerializer, GroupSerializer, \
        GroupListSerializer


@permission_classes((permissions.AllowAny, ))
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    def get_queryset(self):
        return Association.objects.exclude_deleted().filter_events().filter(public=True) \
            .filter_group_containers()

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action == 'retrieve':
            return EventRetrieveSerializer
        return EventRetrieveSerializer


@permission_classes((permissions.AllowAny, ))
class TransitionGroupSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return GroupListSerializer
        return GroupSerializer
