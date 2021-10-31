from django.urls import reverse
from rest_framework import serializers

from grouprise.features.associations.models import Association
from grouprise.features.groups.models import Group


class EventListSerializer(serializers.HyperlinkedModelSerializer):
    timestamp = serializers.SerializerMethodField()
    permalink = serializers.SerializerMethodField()

    def get_timestamp(self, obj):
        return int(obj.container.versions.last().time_created.timestamp())

    def get_permalink(self, obj):
        return self.context["request"].build_absolute_uri(
            reverse("content-permalink", args=(obj.pk,))
        )

    class Meta(object):
        model = Association
        fields = ("id", "permalink", "timestamp")


class EventRetrieveSerializer(EventListSerializer):
    orgId = serializers.SerializerMethodField()  # noqa: N815
    iCal = serializers.SerializerMethodField()  # noqa: N815

    def get_orgId(self, obj):
        return obj.entity.id

    def get_iCal(self, obj):
        ical = "BEGIN:VEVENT\n"
        ical += "UID:%s\n" % obj.container.id
        ical += "LOCATION:%s\n" % obj.container.place
        ical += "SUMMARY:%s\n" % obj.container.title
        ical += "CATEGORIES:\n"
        ical += "DESCRIPTION:%s\n" % obj.container.versions.last().text
        ical += "DTSTART:%s\n" % obj.container.time.strftime("%Y%m%dT%H%m%sZ")
        until_time = obj.container.until_time
        if until_time:
            ical += "DTEND:%s\n" % until_time.strftime("%Y%m%dT%H%m%sZ")
        ical += "DTSTAMP:%s\n" % obj.container.versions.last().time_created.strftime(
            "%Y%m%dT%H%m%sZ"
        )
        ical += "END:VEVENT\n"
        return ical

    class Meta:
        model = Association
        fields = ("id", "permalink", "timestamp", "orgId", "iCal")


class GroupListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    permalink = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    def get_permalink(self, obj: Group):
        return self.context["request"].build_absolute_uri(obj.get_absolute_url())

    def get_timestamp(self, obj: Group):
        return int(obj.time_modified.timestamp())

    class Meta:
        model = Group
        fields = ("id", "permalink", "timestamp")


class GroupSerializer(GroupListSerializer):
    website = serializers.CharField(source="url", read_only=True)
    categories = serializers.SerializerMethodField()
    admins = serializers.SerializerMethodField()
    slogan = serializers.SerializerMethodField()
    locations = serializers.SerializerMethodField()

    def get_categories(self, obj: Group):
        return []

    def get_admins(self, obj: Group):
        return []

    def get_slogan(self, obj: Group):
        return None

    def get_locations(self, obj: Group):
        address = (
            ", ".join(obj.address.replace("\r", "").split("\n"))
            if obj.address
            else None
        )
        return [{"address": address, "description": None, "geo": None}]

    class Meta:
        model = Group
        fields = (
            "id",
            "permalink",
            "timestamp",
            "name",
            "description",
            "admins",
            "categories",
            "website",
            "slogan",
            "locations",
        )
