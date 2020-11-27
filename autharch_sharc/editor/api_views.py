from django_elasticsearch_dsl_drf.filter_backends import (
    FilteringFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    CompoundSearchFilterBackend,
    SuggesterFilterBackend
)
from django_elasticsearch_dsl_drf.viewsets import (
    DocumentViewSet, ReadOnlyModelViewSet
)
from elasticsearch_dsl import (
    HistogramFacet,
    DateHistogramFacet,
    TermsFacet,
    NestedFacet
)

from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from rest_framework import permissions
from rest_framework.response import Response

from .documents import EADDocument
from .serializers import EADDocumentResultSerializer

ES_FACET_OPTIONS = {"order": {"_key": "asc"}, "size": 100}


class EADDocumentViewSet(DocumentViewSet):
    document = EADDocument
    serializer_class = EADDocumentResultSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    lookup_field = "id"

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
        'related_sources.works',
        'related_sources.texts',
        'related_sources.performances',
        'related_sources.sources',
        "acquirer"
    )

    filter_fields = {
        'pk': 'pk',
        'unittitle': 'unittitle.raw',
        'date_of_creation': 'date_of_creation',
        'date_of_acquisition': 'date_of_acquisition',
        'category': 'category.lowercase',
        "acquirer": "related_people.acquirers",
        'work': 'related_sources.works',
        'text': 'related_sources.texts',
        'performance': 'related_sources.performances',
        'sources': 'related_sources.sources',
    }

    faceted_search_fields = {
        'category': {
            'facet': TermsFacet,
            'field': 'category.lowercase',
            'enabled': True,
            'options': ES_FACET_OPTIONS
        },
        "acquirer": {
            'facet': TermsFacet,
            'field': "related_people.acquirers",
            'enabled': True,
            'options': ES_FACET_OPTIONS
        },
        'individual_connections': {
            'facet': TermsFacet,
            'field': 'related_sources.individuals',
            'enabled': True,
            'options': ES_FACET_OPTIONS
        },
        'work': {
            'facet': TermsFacet,
            'field': 'related_sources.works',
            'enabled': True,
            'options': ES_FACET_OPTIONS
        },
        'text': {
            'facet': TermsFacet,
            'field': 'related_sources.texts',
            'enabled': True,
            'options': ES_FACET_OPTIONS
        },
        'performance': {
            'facet': TermsFacet,
            'field': 'related_sources.performances',
            'enabled': True,
            'options': ES_FACET_OPTIONS
        },
        'source': {
            'facet': TermsFacet,
            'field': 'related_sources.sources',
            'enabled': True,
            'options': ES_FACET_OPTIONS
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
        'category_suggest': {
            'field': 'category.suggest',
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @classmethod
    def _data_to_retrieve_response(cls, data):
        """ Repackage the document data for the vue response"""
        # related_sources = {}
        # if ('individual_connections' in data and data[
        #     'individual_connections'
        # ] is not None):
        #     related_sources['individual_connections'] = data[
        #         'individual_connections']
        # if ('work_connections' in data and data[
        #     'work_connections'
        # ] is not None):
        #     related_sources['works'] = data['work_connections']
        # if ('text_connections' in data and data[
        #     'text_connections'
        # ] is not None):
        #     related_sources['texts'] = data['text_connections']
        # if ('performance_connections' in data and data[
        #     'performance_connections'
        # ] is not None):
        #     related_sources['performances'] = data[
        #         'performance_connections']
        # if ('source_connections' in data and data[
        #     'source_connections'
        # ] is not None):
        #     related_sources['sources'] = data['source_connections']
        # data['related_sources'] = related_sources


        # related_people = {}
        # if ('donor' in data and data['donor'] is not None):
        #     related_sources['donors'] = data['donor']
        # if ('acquirer' in data and data['acquirer'] is not None):
        #     related_sources['acquirers'] = data['acquirer']
        # data['related_people'] = related_people
        return data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(self._data_to_retrieve_response(serializer.data))
