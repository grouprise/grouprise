from django.urls import reverse
from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import permission_classes

from core import api
from features.associations.models import Association


class EventListSerializer(serializers.HyperlinkedModelSerializer):
    timestamp = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()

    def get_timestamp(self, obj):
        return int(obj.container.versions.last().time_created.timestamp())

    def get_permalink(self, obj):
        return self.context['request'].build_absolute_uri(
                reverse('content-permalink', args=(obj.pk,)))

    class Meta(object):
        model = Association
        fields = ('id', 'permalink', 'timestamp')


class EventRetrieveSerializer(EventListSerializer):
    orgId = serializers.SerializerMethodField()
    iCal = serializers.SerializerMethodField()

    def get_orgId(self, obj):
        return obj.entity.id

    def get_iCal(self, obj):
        ical = "BEGIN:VEVENT\n"
        ical += "UID:%s\n" % obj.container.id
        ical += "LOCATION:%s\n" % obj.container.place
        ical += "SUMMARY:%s\n" % obj.container.title
        ical += "CATEGORIES:\n"
        ical += "DESCRIPTION:%s\n" % obj.container.versions.last().text
        ical += "DTSTART:%s\n" % obj.container.time.strftime('%Y%m%dT%H%m%sZ')
        until_time = obj.container.until_time
        if until_time:
            ical += "DTEND:%s\n" % until_time.strftime('%Y%m%dT%H%m%sZ')
        ical += "DTSTAMP:%s\n" % obj.container.versions.last().time_created \
                .strftime('%Y%m%dT%H%m%sZ')
        ical += "END:VEVENT\n"
        return ical

    class Meta:
        model = Association
        fields = ('id', 'permalink', 'timestamp', 'orgId', 'iCal')


@permission_classes((permissions.AllowAny, ))
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Association.objects.exclude_deleted().filter_events().filter(public=True) \
            .filter_group_containers()

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action == 'retrieve':
            return EventRetrieveSerializer
        return EventRetrieveSerializer


@api.register_tc
def load(router):
    router.register(r'event', EventViewSet, 'event')
