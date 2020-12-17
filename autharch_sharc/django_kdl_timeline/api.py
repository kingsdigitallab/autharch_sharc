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
# Add the three endpoints using the "register_endpoint" method.
# The first parameter is the name of the endpoint (eg. pages, images). This
# is used in the URL of the endpoint
# The second parameter is the endpoint class that handles the requests

# api_router.register_endpoint('documents', DocumentsAPIViewSet)
