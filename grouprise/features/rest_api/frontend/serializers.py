import django
from rest_framework import serializers
from taggit.models import Tag

from grouprise import core
from grouprise.features.gestalten.models import Gestalt, GestaltSetting
from grouprise.features.groups.models import Group
from grouprise.features.images.models import Image


def validate_file_size(image):
    try:
        core.models.validate_file_size(image['file'])
    except django.forms.ValidationError as e:
        raise serializers.ValidationError(e)


class GestaltSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='__str__', read_only=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)

    class Meta:
        model = Gestalt
        fields = ('id', 'name', 'initials', 'about', 'avatar', 'avatar_color', 'url')


class GestaltOrAnonSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        if 'id' in data and data['id'] is not None:
            return Gestalt.objects.get(pk=data['id'])
        # todo validate name if no valid id was provided
        return data

    def run_validators(self, value):
        """ the 'run_validators' method of serializers.Serializer seems to expect a dict """
        if not isinstance(value, dict):
            value = {'id': value.id, 'name': value.name}
        return super().run_validators(value)

    class Meta:
        fields = ('id', 'name')


class GestaltSettingSerializer(serializers.ModelSerializer):
    def get_fields(self):
        fields = super().get_fields()
        gestalt = self.context['view'].request.user.gestalt
        fields['gestalt'].queryset = Gestalt.objects.filter(id=gestalt.id)
        return fields

    class Meta:
        model = GestaltSetting
        fields = ('id', 'gestalt', 'name', 'category', 'value')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name')


class GroupSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    initials = serializers.CharField(source='get_initials', read_only=True)
    url = serializers.CharField(source='get_absolute_url', read_only=True)
    cover = serializers.SerializerMethodField()

    def get_cover(self, obj: Group):
        return obj.get_cover_url()

    class Meta:
        model = Group
        fields = ('id', 'slug', 'name', 'initials', 'description', 'avatar',
                  'avatar_color', 'tags', 'cover', 'url', )


class ImageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='file.name', read_only=True)
    path = serializers.CharField(source='file.url', read_only=True)

    class Meta:
        model = Image
        fields = ('id', 'file', 'title', 'creator', 'path')
        validators = [validate_file_size]

    def _get_gestalt(self):
        try:
            return self.context['request'].user.gestalt
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
        repr['preview'] = instance.preview_api.url
        return repr
