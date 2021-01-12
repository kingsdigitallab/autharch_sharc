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
            # creation_date_notes: "creation_date_note",
            "place_of_origin",
            "date_of_acquisition",
            # acquisition_dates_notes
            #  provenance: "provenance",
            # 'connection_primary',
            # 'connection_secondary',
            # 'connection_type',
            # 'publicationstatus_value',
            "related_material",
            "related_sources",
            "related_people",
            "media",
        )
