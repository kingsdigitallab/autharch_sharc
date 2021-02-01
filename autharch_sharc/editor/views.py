from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, TemplateView

from ead.models import (
    EAD, MaintenanceEvent, OriginationCorpName, OriginationFamName,
    OriginationName, OriginationPersName)

from elasticsearch_dsl import FacetedSearch, TermsFacet

import reversion
from reversion.models import Revision, Version

from . import forms
from .documents import EADDocument
from .generic_views import SearchView


def output_error_log(form, indent=0):
    for field, field_errors in form.errors.items():
        print('{}{}: {}'.format(' ' * indent, field, field_errors))
    if hasattr(form, 'formsets'):
        for formset in form.formsets.values():
            print('{}{}: {}'.format(' ' * indent, type(formset),
                                    formset.is_valid()))
            for form in formset.forms:
                output_error_log(form, indent+2)


class FacetMixin:

    facet_key = 'facets'  # GET querystring name for facet name/value pairs

    def _annotate_facets(self, facets, query_dict):
        """Return a dictionary of `facets` annotated with links to apply or
        unapply the facet values, and facet value names where these
        differ from the facet value. Also return a list of selected
        facet values.

        `facets` is a dictionary keyed by facet name, with each value
        a list of tuples of key, document count, and a Boolean
        indicating whether the key (facet value) is selected.

        """
        selected_facets = []
        for facet_name in facets:
            display_values = None
            if facet_name == 'creators':
                display_values = {
                    'corpname': OriginationCorpName,
                    'famname': OriginationFamName,
                    'name': OriginationName,
                    'persname': OriginationPersName,
                }
            for idx, (value, count, selected) in enumerate(facets[facet_name]):
                if selected:
                    link = self._create_unapply_link(
                        facet_name, value, query_dict)
                else:
                    link = self._create_apply_link(
                        facet_name, value, query_dict)
                if display_values is None:
                    display_value = value
                else:
                    if facet_name == 'creators':
                        creator_type, pk = value.split('-')
                        display_value = display_values[creator_type].objects.get(pk=pk).assembled_name
                new_data = (display_value, count, link, selected)
                facets[facet_name][idx] = new_data
                if selected:
                    selected_facets.append(new_data)
        return facets, selected_facets

    def _create_apply_link(self, facet_name, value, query_dict):
        """Return a querystring to apply the facet `value` to the existing
        querystring in `query_dict`."""
        new_facet = '{}:{}'.format(facet_name, value)
        qd = query_dict.copy()
        facets = qd.getlist(self.facet_key)
        facets.append(new_facet)
        qd.setlist(self.facet_key, facets)
        link = '?{}'.format(qd.urlencode())
        return link

    def _create_unapply_link(self, facet_name, value, query_dict):
        """Return a querystring to unapply the facet `value` from the existing
        querystring in `query_dict`."""
        old_facet = '{}:{}'.format(facet_name, value)
        qd = query_dict.copy()
        facets = qd.getlist(self.facet_key)
        facets.remove(old_facet)
        qd.setlist(self.facet_key, facets)
        link = qd.urlencode()
        if link:
            link = '?{}'.format(link)
        else:
            link = '.'
        return link

    def _split_selected_facets(self, selected_facets):
        """Return a dictionary of selected facet values keyed by the facet
        each belongs to."""
        split_facets = {}
        for selected_facet in selected_facets:
            facet, value = selected_facet.split(':', maxsplit=1)
            split_facets.setdefault(facet, []).append(value)
        return split_facets


class HomeView(LoginRequiredMixin, TemplateView):

    template_name = "editor/home.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["current_section"] = 'home'
        context['modified'] = self._get_modified_records(self.request.user)
        return context

    def _get_modified_records(self, user):
        versions = Version.objects.get_for_model(EAD).filter(
            revision__user=user)
        record_ids = [version.object_id for version in versions]
        return EAD.objects.filter(id__in=record_ids)


class RecordHistory(LoginRequiredMixin, DetailView):

    model = EAD
    template_name = 'editor/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_section"] = 'records'
        context['edit_url'] = reverse('editor:record-edit',
                                      kwargs={'record_id': self.object.pk})
        context['versions'] = Version.objects.get_for_object(self.object)
        return context


class RecordSearch(FacetedSearch):
    doc_types = [EADDocument]
    facets = {
        'categories': TermsFacet(field='category'),
        'connections_primary': TermsFacet(field='connection_primary'),
        'connections_secondary': TermsFacet(field='connection_secondary'),
        'connection_types': TermsFacet(field='connection_type'),
        'creators': TermsFacet(field='creators.key', size=10),
    }
    fields = ['creators.name', 'unittitle']


class RecordList(LoginRequiredMixin, SearchView, FacetMixin):

    context_object_name = "records"
    form_class = forms.EADRecordSearchForm
    search_class = RecordSearch
    template_name = "editor/record_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_section"] = 'records'
        return context


@login_required
def record_edit(request, record_id):
    record = get_object_or_404(EAD, pk=record_id)
    form_errors = []
    if request.method == 'POST':
        form = forms.RecordEditForm(request.POST, instance=record)
        if form.is_valid():
            with reversion.create_revision():
                form.save()
                #reversion.set_user(self.request.user)
                reversion.set_comment('Edited')
            url = reverse('editor:record-edit',
                          kwargs={'record_id': record_id}) + '?saved=true'
            return redirect(url)
        else:
            form_errors = forms.assemble_form_errors(form)
    else:
        form = forms.RecordEditForm(instance=record)
    context = {
        'current_section': 'records',
        'form': form,
        'form_errors': form_errors,
        'record': record,
        'reverted': request.GET.get('reverted', False),
        'saved': request.GET.get('saved', False),
    }
    return render(request, 'editor/record_edit.html', context)


@login_required
def revert(request):
    revision_id = request.POST.get('revision_id')
    revision = get_object_or_404(Revision, pk=revision_id)
    revision.revert(delete=True)
    return redirect(request.POST.get('redirect_url')
                    + '?reverted={}'.format(revision_id))
