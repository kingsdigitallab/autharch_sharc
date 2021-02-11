from django.urls import path

from . import views

app_name = "editor"

home_view = views.HomeView.as_view()
record_history = views.RecordHistory.as_view()
record_list = views.RecordList.as_view()

urlpatterns = [
    path("", home_view, name="home"),
    path("records/", record_list, name="record-list"),
    path("records/new/", views.record_create, name="record-create"),
    path("records/<int:record_id>/", views.record_edit, name="record-edit"),
    path("records/<int:pk>/history/", record_history, name="record-history"),
    path("revert/", views.revert, name="revert"),
]
