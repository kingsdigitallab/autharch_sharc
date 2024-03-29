from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from autharch_sharc.editor import api_views
from config.api_router import wagtail_api_router

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("autharch_sharc.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("vocabularies/", include("controlled_vocabulary.urls")),
    path("api/wagtail/", wagtail_api_router.urls),
    path("editor/", include("autharch_sharc.editor.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    path(
        r"api/events/", api_views.SharcListTimelineEvents.as_view(), name="event-list"
    ),
    # path(r"api/stories/", api_views.StoryView.as_view(), name="story-list"),
    # API base url
    path("api/", include("config.api_router")),
    re_path(
        r"^rct/(?P<path>.*)$",
        api_views.simple_proxy,
        {"target_url": "https://rct.resourcespace.com/"},
    ),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
]

# Wagtail URLS
urlpatterns += [
    re_path("wagtail/", include(wagtailadmin_urls)),
    re_path("documents/", include(wagtaildocs_urls)),
    re_path("", include(wagtail_urls)),
]


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
