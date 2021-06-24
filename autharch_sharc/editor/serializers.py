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

    class Meta:
        document = EADDocument

        fields = (
            "pk",
            "reference",
            "unittitle",
            "category",
            "size",
            "medium",
            "label",
            "creators",
            "date_of_creation",
            "date_of_creation_notes",
            "place_of_origin",
            "date_of_acquisition",
            "date_of_acquisition_notes",
            "related_material",
            "related_sources",
            "related_people",
            "media",
            "search_content",
            "doc_type",
            "stories",
            "notes",
            "provenance",
            "references_published",
            "references_unpublished",
        )
