import json

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers

from .documents import EADDocument


class EADDocumentThemeResultSerializer(DocumentSerializer):
    id = serializers.IntegerField(source="pk", read_only=True)
    title = serializers.CharField(read_only=True, source="unittitle")
    creators = serializers.SerializerMethodField()
    creation_date = serializers.SerializerMethodField()
    resource = serializers.SerializerMethodField()

    class Meta:
        document = EADDocument

        fields = (
            "reference",
            "category",
            # "size",
            # "medium",
            # "label",
            # "creators",
            # ,
            # "media",
        )

    def get_resource(self, obj):
        if obj.media:
            for m in obj.media:
                return m.thumbnail_url
        return ""

    def get_creators(self, obj):
        if obj.creators:
            creators = list()
            for c in obj.creators:
                creators.append(c.name)
            return creators
        else:
            return []

    def get_creation_date(self, obj):
        if obj.date_of_creation:
            return obj.date_of_creation[0]
        else:
            return []


class EADDocumentResultSerializer(DocumentSerializer):
    """ Serializer for EAD XML document"""

    media = serializers.SerializerMethodField()

    class Meta:
        document = EADDocument

        fields = (
            "pk",
            "reference",
            "rct_link",
            "unittitle",
            "size",
            "medium",
            "label",
            "creators",
            "date_of_creation",
            "date_of_creation_range",
            "date_of_creation_notes",
            "place_of_origin",
            "date_of_acquisition",
            "date_of_acquisition_range",
            "date_of_acquisition_notes",
            "related_parsed",
            "related_material",
            "related_material_parsed",
            "related_sources",
            "related_people",
            # "media",
            "search_content",
            "doc_type",
            "stories",
            "notes",
            "notes_parsed",
            "provenance",
            # "category",
            "references_published",
            "references_unpublished",
        )

    def get_media(self, obj):
        media = obj.media
        media_list = list()

        for m in media:
            # this is, not great, but I can't get it to accept that it's json
            # otherwise
            media_list.append(
                {
                    "label": m.label,
                    "iiif_manifest_url": m.iiif_manifest_url,
                    "iiif_image_url": m.iiif_image_url,
                    "full_image_url": m.full_image_url,
                    "thumbnail_url": m.thumbnail_url,
                    "image_width": m.image_width,
                    "image_height": m.image_height,
                    "thumbnail_width": m.thumbnail_width,
                    "thumbnail_height": m.thumbnail_height,
                    "order": m.order,
                }
            )
        # make sure we're sorted by order
        sortedList = sorted(media_list, key=lambda d: d["order"])

        return sortedList
