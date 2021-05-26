"""
API for timeline server through Wagtail
(From
https://docs.wagtail.io/en/v2.11.3/advanced_topics/api/v2/configuration.html)
"""

from rest_framework import permissions
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet


class SharcPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


wagtail_api_router = WagtailAPIRouter("wagtailapi")
wagtail_api_router.register_endpoint("images", ImagesAPIViewSet)
wagtail_api_router.register_endpoint("pages", SharcPagesAPIViewSet)
wagtail_api_router.register_endpoint("documents", DocumentsAPIViewSet)
