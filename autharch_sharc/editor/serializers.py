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

    place_of_origin = serializers.SerializerMethodField()
    references_published = serializers.SerializerMethodField()
    # references_unpublished = serializers.SerializerMethodField()

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
            # "place_of_origin",
            "date_of_acquisition",
            "date_of_acquisition_range",
            "date_of_acquisition_notes",
            "related_parsed",
            "related_material",
            "related_sources",
            "related_people",
            "media",
            "search_content",
            "doc_type",
            "stories",
            "notes",
            "provenance",
            # "category",
            # "references_published",
            # "references_unpublished",
        )

    def get_place_of_origin(self, obj):
        try:
            if obj.place_of_origin:
                return obj.place_of_origin
            else:
                return None
        except AttributeError:
            return None

    def get_references_published(self, obj):
        try:
            if obj.references_published:
                return obj.references_published
            else:
                return []
        except AttributeError:
            return None

    def get_references_unpublished(self, obj):
        try:
            if obj.references_unpublished:
                return obj.references_unpublished
            else:
                return []
        except AttributeError:
            return []
