from django.urls import path

from . import views


app_name = 'editor'

home_view = views.HomeView.as_view()
record_history = views.RecordHistory.as_view()
record_list = views.RecordList.as_view()

urlpatterns = [
    path(r'', home_view, name='home'),
    path(r'records/', record_list, name='record-list'),
    path(r'records/<int:record_id>/', views.record_edit, name='record-edit'),
    path(r'records/<int:pk>/history/', record_history,
         name='record-history'),
    path('revert/', views.revert, name='revert'),
]
