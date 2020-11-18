from rest_framework import permissions
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from .documents import EADDocument
from .serializers import EADDocumentSerializer


class EADDocumentViewSet(DocumentViewSet):
    document = EADDocument
    serializer_class = EADDocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    lookup_field = "id"

    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]

    search_fields = (
        'unittitle',
        'category',
        'date_of_creation',
        'date_of_acquisition',
        'connection_primary',
        'creators'
    )

    filter_fields = {
        'pk': 'pk',
        'unittitle': 'unittitle.raw',
        'date_of_creation': 'date_of_creation'
    }

    ordering_fields = {
        'unittitle': 'unittitle.sort',
        'date_of_creation': 'date_of_creation'
    }

    

    ordering = ('unittitle', 'date_of_creation')
