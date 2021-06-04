from django.urls import path

from . import views

app_name = "editor"

record_history = views.RecordHistory.as_view()
record_list = views.RecordList.as_view()
deleted_record_list = views.RecordDeletedListView.as_view()

urlpatterns = [
    path("", views.home, name="home"),
    path("records/", record_list, name="record-list"),
    path("records/deleted/", deleted_record_list, name="record-deleted-list"),
    path("records/new/", views.record_create, name="record-create"),
    path("records/<int:record_id>/", views.record_edit, name="record-edit"),
    path("records/<int:record_id>/delete/", views.record_delete,
         name="record-delete"),
    path("records/<int:pk>/history/", record_history, name="record-history"),
    path("revert/", views.revert, name="revert"),
]
