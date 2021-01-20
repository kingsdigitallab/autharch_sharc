from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import EADDocument


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
            "place_of_origin",
            "date_of_acquisition",
            "related_material",
            "related_sources",
            "related_people",
            "media",
            "search_content",
            "doc_type"
        )
