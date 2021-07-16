import mimetypes

import urllib3
from django.http import HttpResponse
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    MultiMatchSearchFilterBackend,
    OrderingFilterBackend,
    SuggesterFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import TermsFacet
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from autharch_sharc.django_kdl_timeline.views import ListTimelineEvents
from autharch_sharc.editor.models import SharcTimelineEventSnippet

from .documents import EADDocument
from .serializers import EADDocumentResultSerializer, EADDocumentThemeResultSerializer

ES_FACET_OPTIONS = {"order": {"_key": "asc"}, "size": 100}


class SharcListTimelineEvents(ListTimelineEvents):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    model = SharcTimelineEventSnippet


def simple_proxy(request, path, target_url):
    url = "%s%s" % (target_url, path)
    if "QUERY_STRING" in request.META and len(request.META["QUERY_STRING"]) > 0:
        url += "?" + request.META["QUERY_STRING"]
    try:
        http = urllib3.PoolManager()
        proxied_request = http.request("GET", url)
        status_code = proxied_request.status
        if "content-type" in proxied_request.headers:
            mimetype = proxied_request.headers["content-type"]
        else:
            mimetype = proxied_request.headers.typeheader or mimetypes.guess_type(url)
        content = proxied_request.data.decode("utf-8")
    except urllib3.exceptions.HTTPError as e:
        return HttpResponse(e.msg, status=e.code, content_type="text/plain")
    else:
        return HttpResponse(content, status=status_code, content_type=mimetype)


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
        MultiMatchSearchFilterBackend,
        # the suggester backend needs to be the last backend
        SuggesterFilterBackend,
    ]

    search_fields = ("search_content",)

    multi_match_search_fields = {
        "unittitle": {"boost": 4},
        "reference.text": {"boost": 5},
        "notes.raw": None,
        "label.text": None,
        "references_published.reference": None,
        "references_unpublished.reference": None,
        "related_people.all_people.name": None,
        "related_people.acquirers": None,
    }

    multi_match_options = {"type": "phrase_prefix"}

    filter_fields = {
        "pk": "pk",
        "reference": "reference",
        "unittitle": "unittitle.raw",
        "date_of_creation": "date_of_creation",
        "date_of_acquisition": "date_of_acquisition",
        "category": "category.lowercase",
        "themes": "themes.raw",
        "acquirer": "related_people.acquirers.raw",
        "people": "related_people.all_people.facet_label",
        "work": "related_sources.works",
        "text": "related_sources.texts",
        "performance": "related_sources.performances",
        "sources": "related_sources.sources",
        "individual_connections": "related_sources.individuals",
        "doc_type": "doc_type",
        "stories": "stories.story",
        "provenance": "provenance.raw",
    }

    faceted_search_fields = {
        "category": {
            "facet": TermsFacet,
            "field": "category",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "themes": {
            "facet": TermsFacet,
            "field": "themes.raw",
            "enabled": False,
            "options": ES_FACET_OPTIONS,
        },
        "creator": {
            "facet": TermsFacet,
            "field": "creators.name",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "acquirer": {
            "facet": TermsFacet,
            "field": "related_people.acquirers.raw",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "people": {
            "facet": TermsFacet,
            "field": "related_people.all_people.facet_label",
            "enabled": True,
            "options": {"order": {"_key": "asc"}, "size": 5000},
        },
        "individual_connections": {
            "facet": TermsFacet,
            "field": "related_sources.individuals",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "work": {
            "facet": TermsFacet,
            "field": "related_sources.works",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "text": {
            "facet": TermsFacet,
            "field": "related_sources.texts",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "performance": {
            "facet": TermsFacet,
            "field": "related_sources.performances",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "source": {
            "facet": TermsFacet,
            "field": "related_sources.sources",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
    }

    # Suggester fields
    suggester_fields = {
        "unittitle_suggest": {
            "field": "unittitle.suggest",
            "suggesters": [
                SUGGESTER_COMPLETION,
            ],
            "options": {
                "size": 20,  # Override default number of suggestions
                "skip_duplicates": True,
                # Whether duplicate suggestions should be filtered out.
            },
        },
        "category_suggest": {
            "field": "category.suggest",
            "suggesters": [
                SUGGESTER_COMPLETION,
            ],
            "options": {
                "size": 20,  # Override default number of suggestions
                "skip_duplicates": True,
                # Whether duplicate suggestions should be filtered out.
            },
        },
        "person_suggest": {
            "field": "related_people.all_people.name.suggest",
            "suggesters": [
                SUGGESTER_COMPLETION,
            ],
            "options": {
                "size": 20,
                "skip_duplicates": True,
            },
        },
    }

    ordering_fields = {
        "unittitle": "unittitle.sort",
        "date_of_creation": "date_of_creation",
        "date_of_acquisition": "date_of_acquisition",
    }

    ordering = (
        "_score",
        "unittitle.sort",
    )

    def get_doc_type_queryset(self):
        # Include only objects in this search
        return (
            self.filter_queryset(self.get_queryset())
            .filter(
                "terms",
                doc_type=["object"],
            )
            .filter("match", is_visible=True)
        )

    @classmethod
    def _filter_person_facet(cls, autocomplete_search, response):
        if (
            "facets" in response.data
            and "_filter_people" in response.data["facets"]
            and len(response.data["facets"]["_filter_people"]) > 0
        ):
            person_facets = response.data["facets"]["_filter_people"]["people"][
                "buckets"
            ]
            filtered_persons = list()
            for person_facet in person_facets:
                if (
                    str(person_facet["key"])
                    .lower()
                    .startswith(autocomplete_search.lower())
                ):
                    # Remove person from facet results, not relevant
                    filtered_persons.append(person_facet)
            if len(filtered_persons) > 100:
                response.data["facets"]["_filter_people"]["people"][
                    "buckets"
                ] = filtered_persons[0:101]
            else:
                response.data["facets"]["_filter_people"]["people"][
                    "buckets"
                ] = filtered_persons
        return response

    def list(self, request, *args, **kwargs):
        queryset = self.get_doc_type_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(self._data_to_list(serializer.data))
        else:
            serializer = self.get_serializer(queryset, many=True)
            response = Response(data=self._data_to_list(serializer.data))
        if "person_autocomplete" in self.request.GET:
            # filter the person facet with autocomplete string
            person_autocomplete = self.request.GET["person_autocomplete"]
            response = EADDocumentViewSet._filter_person_facet(
                person_autocomplete, response
            )

        return response

    @classmethod
    def _data_to_list(cls, data):
        if "media" in data and data["media"] is not None:
            if len(data["media"]) > 0:
                # Only include first item in media
                # todo look at ordering/priority of items
                # when we have more data
                data["media"] = data["media"][0]
        return data

    @classmethod
    def _data_to_retrieve(cls, data):
        """ Extra data transformations for single record view"""
        if "creators" in data and data["creators"] is not None:
            # Remove keys as they're not needed for display
            filtered_creators = []
            for creator in data["creators"]:
                filtered_creators.append(creator["name"])
            data["creators"] = filtered_creators

        return data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(data=self._data_to_retrieve(serializer.data))


class SharcSiteSearch(EADDocumentViewSet):
    """
    Provides searches on documents and wagtail objects
         in one response"""

    def get_doc_type_queryset(self):
        # Include all objects in this search
        return self.filter_queryset(self.get_queryset())


class EditorTableView(APIView):
    """
    Return rows for the table in the editor

    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = EADDocumentResultSerializer

    def document_search(self, request, **kwargs):
        """Get all documents with a theme
        aggregate them into lists by theme"""
        # docviewset = EADDocumentViewSet()
        # s = Search(index=docviewset.index, using=docviewset.client)
        # response = s.query(Exists(field="themes.raw")).execute()
        # themes_results = dict()
        # Collate response into different themes
        results = list()
        for h in kwargs["records"]:
            results.append(EADDocumentThemeResultSerializer(h).data)

        return results

    def get(self, request, *args, **kwargs):
        results = self.document_search(request, **kwargs)
        return Response({"count": kwargs["results_count"], "results": results})
