from rest_framework import serializers

from grouprise.features.gestalten.models import Gestalt, GestaltSetting


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
