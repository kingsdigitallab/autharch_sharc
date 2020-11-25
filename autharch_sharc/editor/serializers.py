from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import EADDocument


class EADDocumentSerializer(DocumentSerializer):
    """ Serializer for EAD XML document"""

    class Meta:
        document = EADDocument

    fields = (
        'pk',
        'creators'
        # 'category',
        # 'connection_primary',
        # 'connection_secondary',
        # 'connection_type',
        'date_of_acquisition',
        'date_of_creation',
        # 'publicationstatus_value',
        'unittitle'
    )
