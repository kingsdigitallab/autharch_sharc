from django.urls import path

from . import api_views, views

app_name = "editor"

record_list = views.RecordList.as_view()
record_wizard = views.RecordWizard.as_view(url_name="editor:record-wizard-step")

urlpatterns = [
    path(r"records/", record_list, name="record-list"),
    path(r"records/<int:record_id>/", record_wizard, name="record-wizard"),
    path(
        "records/<int:record_id>/<str:step>/", record_wizard, name="record-wizard-step"
    ),
    path(r"events/", api_views.SharcListTimelineEvents.as_view(), name="event-list"),
]
