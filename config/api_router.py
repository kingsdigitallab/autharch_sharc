from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from autharch_sharc.editor.api_views import (
    EADDocumentViewSet,
    SharcSiteSearch,
)
from autharch_sharc.users.api.views import UserViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register(r"documents", EADDocumentViewSet, basename="eaddocument")
router.register(r"search", SharcSiteSearch, basename="sitesearch")
app_name = "api"
urlpatterns = router.urls
