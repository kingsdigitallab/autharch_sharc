from django.conf import settings
from rest_framework import permissions
from rest_framework.routers import DefaultRouter, SimpleRouter
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.documents.api.v2.views import DocumentsAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet

from autharch_sharc.editor.api_views import EADDocumentViewSet, PersonEADDocumentViewSet
from autharch_sharc.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register(r"documents", EADDocumentViewSet, basename="eaddocument")
router.register(r"persons", PersonEADDocumentViewSet, basename="persondocument")
# router.register(r"search", SharcSiteSearch, basename="sitesearch")
app_name = "api"
urlpatterns = router.urls

"""
API for timeline server through Wagtail
(From
https://docs.wagtail.io/en/v2.11.3/advanced_topics/api/v2/configuration.html)
"""


class SharcPagesAPIViewSet(PagesAPIViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


wagtail_api_router = WagtailAPIRouter("wagtailapi")
wagtail_api_router.register_endpoint("images", ImagesAPIViewSet)
wagtail_api_router.register_endpoint("pages", SharcPagesAPIViewSet)
wagtail_api_router.register_endpoint("documents", DocumentsAPIViewSet)
