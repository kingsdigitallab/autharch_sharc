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

    lookup_field = "pk"

    filter_backends = [
        FilteringFilterBackend,
        IdsFilterBackend,
        OrderingFilterBackend,
        DefaultOrderingFilterBackend,
        SearchFilterBackend,
    ]
