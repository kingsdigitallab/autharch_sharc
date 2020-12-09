from django.urls import path

from . import views


app_name = 'editor'

home_view = views.HomeView.as_view()
entity_list = views.EntityList.as_view()
record_history = views.RecordHistory.as_view()
record_list = views.RecordList.as_view()
record_wizard = views.RecordWizard.as_view(
    url_name='editor:record-wizard-step')

urlpatterns = [
    path(r'', home_view, name='home'),
    path(r'entities/', entity_list, name='entity-list'),
    path(r'entities/<str:entity_type>/<int:entity_id>/', views.entity_edit,
         name='entity-edit'),
    path(r'records/', record_list, name='record-list'),
    path(r'records/<int:record_id>/', record_wizard, name='record-wizard'),
    path(r'records/<int:pk>/history/', record_history,
         name='record-history'),
    path('records/<int:record_id>/<str:step>/', record_wizard,
         name='record-wizard-step'),
    path('revert/', views.revert, name='revert'),
]
