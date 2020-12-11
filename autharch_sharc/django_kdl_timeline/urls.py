from django.urls import path
from.views import ListTimelineEvents

urlpatterns = [
    path(r'events/', ListTimelineEvents.as_view(), name='event-list'),
]
