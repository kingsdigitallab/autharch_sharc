from rest_framework import permissions
from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    SearchFilterBackend,
    FacetedSearchFilterBackend
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import (
    DateHistogramFacet,
    RangeFacet,
    TermsFacet,
)

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
        FacetedSearchFilterBackend
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
        'date_of_creation': 'date_of_creation',
        'category': 'category.raw'
    }

    faceted_search_fields = {
        'category': {
            'facet': TermsFacet,
            'field': 'category.raw',
            'enabled': True
        },
        'connection_primary': {
            'facet': TermsFacet,
            'field': 'connection_primary',
            'enabled': True
        },
        'date_of_creation': {
            'field': 'date_of_creation',
            "enabled": True,
            'facet': DateHistogramFacet,
            'options': {
                'interval': 'year',
            }
        },
        'date_of_acquisition': {
            'field': 'date_of_acquisition',
            "enabled": True,
            'facet': DateHistogramFacet,
            'options': {
                'interval': 'year',
            }
        },
    }

    ordering_fields = {
        'unittitle': 'unittitle.sort',
        'date_of_creation': 'date_of_creation'
    }

    ordering = ('unittitle', 'date_of_creation')
