"""
API for timeline server through Wagtail
(From
https://docs.wagtail.io/en/v2.11.3/advanced_topics/api/v2/configuration.html)
"""

from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.images.api.v2.views import ImagesAPIViewSet

wagtail_api_router = WagtailAPIRouter("wagtailapi")
wagtail_api_router.register_endpoint("images", ImagesAPIViewSet)
wagtail_api_router.register_endpoint("pages", PagesAPIViewSet)
