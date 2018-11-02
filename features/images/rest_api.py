from rest_framework import viewsets, mixins, serializers
from django.db.models import Q

import django
import django_filters
import django_filters.widgets

import core
from core import api
from . import models


def validate_file_size(image):
    try:
        core.models.validate_file_size(image['file'])
    except django.forms.ValidationError as e:
        raise serializers.ValidationError(e)


class ImageFilter(django_filters.rest_framework.FilterSet):
    id = django_filters.Filter(lookup_expr='in', widget=django_filters.widgets.CSVWidget)

    class Meta:
        model = models.Image
        fields = ('id', 'creator')


class ImageSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source='file.name', read_only=True)
    path = serializers.CharField(source='file.url', read_only=True)

    class Meta:
        model = models.Image
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

    def to_representation(self, instance: models.Image):
        repr = super().to_representation(instance)
        repr['preview'] = instance.preview_api.url
        return repr


class ImageSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.ReadOnlyModelViewSet):
    serializer_class = ImageSerializer
    filter_fields = ('id', 'creator')
    filter_class = ImageFilter

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return models.Image.objects.none()

        # FIXME: refactor and remove foreign model queries
        # we want users to have access to
        # * images that they created themselves
        # * images part of a group gallery with user having membership in group
        # * images posted in a group as preview image with user having membership in group
        from features.associations.models import Association
        from features.content.models import Content
        from features.groups.models import Group
        from features.galleries.models import GalleryImage
        from django.contrib.contenttypes.models import ContentType
        from features.memberships.models import Membership
        memberships = Membership.objects.filter(member=user.gestalt)
        groups = Group.objects.filter(memberships__in=memberships)
        associations = Association.objects.filter(
            container_type=ContentType.objects.get_for_model(Content),
            entity_type=ContentType.objects.get_for_model(Group),
            entity_id__in=groups
        )
        group_content = Content.objects.filter(associations__in=associations)
        gallery_images = GalleryImage.objects.filter(
            gallery__in=group_content.filter(gallery_images__isnull=False))
        gallery_image_ids = gallery_images.values_list('image', flat=True)
        preview_images = group_content.filter(image__isnull=False)
        preview_image_ids = preview_images.values_list('image', flat=True)

        return models.Image.objects.filter(
            Q(creator__user=user)  # own images
            | Q(id__in=gallery_image_ids)  # gallery images
            | Q(id__in=preview_image_ids)  # content preview images
        )

    def has_permission(self):
        if self.request.user.is_authenticated:
            if self.action == 'create':
                return True
            elif self.action == 'list':
                return True
            elif self.action == 'retrieve':
                image = self.get_object()
                return self.request.user.has_perm('images.view', image)
            elif self.action == 'update':
                image = self.get_object()
                return image.creator == self.request.user
        return False


@api.register
def load(router):
    router.register(r'images', ImageSet, 'image')
