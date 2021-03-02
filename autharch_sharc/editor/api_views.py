import mimetypes

import urllib3
from django.http import HttpResponse
from django_elasticsearch_dsl_drf.constants import SUGGESTER_COMPLETION
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    DefaultOrderingFilterBackend,
    FacetedSearchFilterBackend,
    FilteringFilterBackend,
    OrderingFilterBackend,
    SuggesterFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from elasticsearch_dsl import Search, TermsFacet
from elasticsearch_dsl.query import Exists
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from autharch_sharc.django_kdl_timeline.views import ListTimelineEvents
from autharch_sharc.editor.models import SharcTimelineEventSnippet

from .documents import EADDocument
from .models import EADDocumentResultSerializer
from .serializers import EADDocumentThemeResultSerializer

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
        # the suggester backend needs to be the last backend
        SuggesterFilterBackend,
    ]

    search_fields = ("search_content",)

    filter_fields = {
        "pk": "pk",
        "reference": "reference",
        "unittitle": "unittitle.raw",
        "date_of_creation": "date_of_creation",
        "date_of_acquisition": "date_of_acquisition",
        "category": "category.lowercase",
        "themes": "themes.raw",
        "acquirer": "related_people.acquirers",
        "work": "related_sources.works",
        "text": "related_sources.texts",
        "performance": "related_sources.performances",
        "sources": "related_sources.sources",
        "individual_connections": "related_sources.individuals",
        "doc_type": "doc_type",
        "stories": "stories.story",
    }

    faceted_search_fields = {
        "category": {
            "facet": TermsFacet,
            "field": "category.raw",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
        },
        "themes": {
            "facet": TermsFacet,
            "field": "themes.raw",
            "enabled": False,
            "options": ES_FACET_OPTIONS,
        },
        "acquirer": {
            "facet": TermsFacet,
            "field": "related_people.acquirers",
            "enabled": True,
            "options": ES_FACET_OPTIONS,
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
    }

    ordering_fields = {
        "unittitle": "unittitle.sort",
        "date_of_creation": "date_of_creation",
    }

    ordering = ("unittitle", "date_of_creation")

    def get_doc_type_queryset(self):
        # Include only objects in this search
        return self.filter_queryset(self.get_queryset()).filter(
            "terms", doc_type=["object"]
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_doc_type_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(self._data_to_list(serializer.data))
            # response["Access-Control-Allow-Origin"] = "*"
            return response

        serializer = self.get_serializer(queryset, many=True)

        return Response(data=self._data_to_list(serializer.data))

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
        if "creators" in data:
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


# class SharcSiteSearch(EADDocumentViewSet):
#     """
#     Provides searches on documents and wagtail objects
#          in one response"""
#
#     def get_doc_type_queryset(self):
#         # Include all objects in this search
#         q= self.filter_queryset(
#             self.get_queryset()).query(MatchPhrasePrefix(themes={"query":
#             "On"}))
#         return self.filter_queryset(self.get_queryset())


class ThemeView(APIView):
    """
    Objects attached to a group e.g. themes

    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def document_search(self, request):
        """Get all documents with a theme
        aggregate them into lists by theme"""
        docviewset = EADDocumentViewSet()
        s = Search(index=docviewset.index, using=docviewset.client)
        response = s.query(Exists(field="themes.raw")).execute()
        themes_results = dict()
        # Collate response into different themes
        for h in response:
            theme = h.themes[0]
            if theme not in themes_results:
                themes_results[theme] = list()
            result = themes_results[theme]
            result.append(EADDocumentThemeResultSerializer(h).data)
            themes_results[theme] = result
        themes = []
        # Refactor into expected api results

        # Will always goes first
        # todo refactor this if we decide to add a theme order
        if "William Shakespeare" in themes_results:
            themes.append(
                {
                    "id": 1,  # no used, kept for clarity
                    "title": "William Shakespeare",
                    "featuredObjects": themes_results["William Shakespeare"],
                }
            )
        # others
        for theme in themes_results.keys():
            if theme != "William Shakespeare":
                themes.append(
                    {
                        "id": 1,  # no used, kept for clarity
                        "title": theme,
                        "featuredObjects": themes_results[theme],
                    }
                )
        return themes

    def get(self, request, *args, **kwargs):
        results = self.document_search(request)
        return Response({"themes": results})


# class SharcListSearchResults(APIView):
#
#
#     search_fields = EADDocumentViewSet.search_fields
#
#     permission_classes = [permissions.IsAuthenticatedOrReadOnly]
#
#     def document_search(self, request):
#         docviewset = EADDocumentViewSet()
#         search = ""
#         s = Search(index=docviewset.index, using=docviewset.client)
#         s = s.highlight_options(order='score')
#         s = s.highlight('search_content', fragment_size=50)
#         if "search" in request.GET:
#             if len(request.GET["search"]) > 0:
#                 search = request.GET["search"]
#             q = MatchPhrasePrefix(search_content={"query": search})
#             response = s.query(q).execute()
#         else:
#             response = s.execute()
#
#         results = list()
#         count = 0
#         for h in response:
#             url = ''
#             description = ''
#             count = response.hits.total['value']
#             highlights = []
#             if h.meta and 'highlight' in h.meta:
#                 for hlight in h.meta.highlight:
#                     highlights.append(hlight)
#             if h.category == 'RichTextPage' or h.category ==
#             'StreamFieldPage':
#                 page = None
#                 if h.category == 'RichTextPage':
#                     page = RichTextPage.objects.get(pk=h.pk)
#                 if h.category == 'StreamFieldPage':
#                     page = StreamFieldPage.objects.get(pk=h.pk)
#                 url = page.full_url
#                 object_type = 'page'
#                 description = h.body
#             else:
#                 object_type = "object"
#                 url = "/objects/" + str(h.pk)
#                 description = h.label
#             results.append({"title": h.unittitle,
#                             "pk": h.pk,
#                             "url": url,
#                             "type:": object_type,
#                             "description": description,
#                             'highlights': highlights
#                             })
#         # rcin_search = EADDocument.search().query("match",
#         # reference=self.RCIN)
#         # response = rcin_search.execute()
#         # for h in response:
#         #
#         # docviewset = EADDocumentViewSet()
#         # docviewset.request = request
#         # response = docviewset.list(request)
#
#         next_page = ''
#         return results, count, next_page
#
#     def get(self, request, *args, **kwargs):
#         results, count, next_page = self.document_search(request)
#         return Response({"results": results,
#                          "count": count,
#                          "next":
#                          "http://127.0.0.1:8000/api/documents/?page=2",
#                          })
