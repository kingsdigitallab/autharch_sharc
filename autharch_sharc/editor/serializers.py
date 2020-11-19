from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from .documents import EADDocument


class EADDocumentSerializer(DocumentSerializer):
    """ Serializer for EAD XML document"""

    class Meta:
        document = EADDocument
