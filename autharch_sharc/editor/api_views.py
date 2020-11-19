from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    CompoundSearchFilterBackend,
    SuggesterFilterBackend
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import (
    DateHistogramFacet,
    TermsFacet,
)

from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from rest_framework import permissions

from .documents import EADDocument
from .serializers import EADDocumentSerializer

ES_FACET_OPTIONS = {"order": {"_key": "asc"}, "size": 100}

from django_elasticsearch_dsl_drf.pagination import (
    PageNumberPagination as BasePageNumberPagination,
)


# https://django-elasticsearch-dsl-drf.readthedocs.io/en/latest/advanced_usage_examples.html?highlight=size#customisations
class RadicalPageNumberPagination(BasePageNumberPagination):
    """Custom page number pagination."""
    page_size_query_param = 'page_size'
    DEFAULT_PAGE_SIZE = 50

    def get_paginated_response_context(self, data):
        __data = super().get_paginated_response_context(data)
        __data.append(("current_page", int(self.request.query_params.get("page", 1))))
        __data.append(("page_size", self.get_page_size(self.request)))
        __data.append(("ordering", self.request.query_params.get("ordering", "")))

        return sorted(__data)

    def get_page_size(self, request):
        size = super().get_page_size(request)


        return self.page_size


class EADDocumentViewSet(DocumentViewSet):
    document = EADDocument
    serializer_class = EADDocumentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    # pagination_class = RadicalPageNumberPagination

    lookup_field = "id"

#    pagination_class = PageNumberPagination

    filter_backends = [
        FilteringFilterBackend,
        FacetedSearchFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        CompoundSearchFilterBackend,
        # the suggester backend needs to be the last backend
        SuggesterFilterBackend,
    ]

    search_fields = (
            'unittitle',
            'category',
            'connection_primary',
    )

    filter_fields = {
            'pk': 'pk',
            'unittitle': 'unittitle.raw',
            'date_of_creation': 'date_of_creation',
            'category': 'category.lowercase'
    }

    faceted_search_fields = {
        'category': {
                'facet': TermsFacet,
                'field': 'category.lowercase',
                'enabled': True,
                'options': ES_FACET_OPTIONS
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

    # Suggester fields
    suggester_fields = {
        'unittitle_suggest': {
            'field': 'unittitle.suggest',
            'suggesters': [
                SUGGESTER_COMPLETION,
            ],
            'options': {
                'size': 20,  # Override default number of suggestions
                'skip_duplicates': True,
                # Whether duplicate suggestions should be filtered out.
            },
        },
    }

    ordering_fields = {
            'unittitle': 'unittitle.sort',
            'date_of_creation': 'date_of_creation'
    }

    ordering = ('unittitle', 'date_of_creation')
