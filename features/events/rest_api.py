from rest_framework import viewsets, serializers, permissions
from rest_framework.decorators import permission_classes

from features.content.models import Content
from core import api


class EventListSerializer(serializers.HyperlinkedModelSerializer):
    timestamp = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()

    def get_timestamp(self, obj):
        latest_version = obj.versions.latest()
        if latest_version:
            return int(latest_version.time_created.timestamp())
        else:
            return None

    def get_permalink(self, obj):
        return self.context['request'].build_absolute_uri(obj.get_absolute_url())

    class Meta(object):
        model = Content
        fields = ('id', 'permalink', 'timestamp')


class EventRetrieveSerializer(EventListSerializer):
    orgId = serializers.SerializerMethodField()
    iCal = serializers.SerializerMethodField()

    def get_orgId(self, obj):
        return obj.get_latest_association().container.id

    def get_iCal(self, obj):
        ical = "BEGIN:VEVENT\n"
        ical += "UID:%s\n" % obj.id
        latest_version = obj.versions.latest()
        if latest_version:
            author = latest_version.author.user
            ical += 'ORGANIZER;CN="%s":MAILTO:%s\n' % (author.get_full_name(), author.email)
        ical += "LOCATION:%s\n" % obj.place
        ical += "SUMMARY:%s\n" % obj.title
        ical += "CATEGORIES:\n"
        # FIXME: Get description
        ical += "DESCRIPTION:%s\n" % ""
        ical += "DTSTART:%s\n" % obj.time.strftime('%Y%m%dT%H%m%sZ')
        ical += "DTEND:%s\n" % obj.until_time.strftime('%Y%m%dT%H%m%sZ')
        if latest_version:
            ical += "DTSTAMP:%s\n" % latest_version.time_created.strftime('%Y%m%dT%H%m%sZ')
        ical += "END:VEVENT\n"
        return ical

    class Meta:
        model = Content
        fields = ('id', 'permalink', 'timestamp', 'orgId', 'iCal')


@permission_classes((permissions.AllowAny, ))
class EventViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Content.objects.filter(time__isnull=False)

    def get_serializer_class(self):
        if self.action == 'list':
            return EventListSerializer
        if self.action == 'retrieve':
            return EventRetrieveSerializer
        return EventRetrieveSerializer


@api.register_tc
def load(router):
    router.register(r'event', EventViewSet, 'event')
