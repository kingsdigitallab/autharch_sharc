from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import DetailView

from ead.models import CorpName, EAD, FamName, MaintenanceEvent, Name, PersName

from elasticsearch_dsl import FacetedSearch, TermsFacet

from formtools.wizard.views import NamedUrlSessionWizardView

import reversion
from reversion.models import Revision, Version

from . import forms
from .documents import EADDocument, EADEntityCorporateBody, EADEntityPerson
from .generic_views import SearchView


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
                    'corpnames': CorpName,
                    'famnames': FamName,
                    'names': Name,
                    'persnames': PersName,
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


class EntitySearch(FacetedSearch):
    doc_types = [EADEntityCorporateBody, EADEntityPerson]
    facets = {
        'entity_type': TermsFacet(field='entity_type.keyword'),
    }
    fields = ['name']


class EntityList(SearchView, FacetMixin):

    context_object_name = "entities"
    form_class = forms.EADEntitySearchForm
    search_class = EntitySearch
    template_name = "editor/entity_list.html"


class HomeView(SearchView, FacetMixin):

    template_name = "editor/home.html"


class RecordHistory(DetailView):

    model = EAD
    template_name = 'editor/history.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['edit_url'] = reverse('editor:record-wizard',
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


class RecordList(SearchView, FacetMixin):

    context_object_name = "records"
    form_class = forms.EADRecordSearchForm
    search_class = RecordSearch
    template_name = "editor/record_list.html"


class RecordWizard(NamedUrlSessionWizardView):
    """Wizard for editing EAD records."""

    form_list = [
        ("contents", forms.EADContentForm),
        ("maintenance", forms.EADMaintenanceForm),
    ]
    TEMPLATES = {
        "contents": "editor/record_wizard_content.html",
        "maintenance": "editor/record_wizard_maintenance.html",
    }

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context["saved"] = self.request.GET.get('saved', False)
        context["record"] = form.instance
        if form.is_bound and not form.is_valid():
            context["form_errors"] = forms.assemble_form_errors(form)
        context["post_data"] = self.request.POST
        context["reverted"] = self.request.GET.get('reverted', False)
        return context

    def done(self, form_list, **kwargs):
        # In order to create a single revision while saving the model
        # instance multiple times, only create a revision when saving
        # the final form.
        for form in list(form_list)[:-1]:
            form.save()
        with reversion.create_revision():
            instance = list(form_list)[-1].save()
            last_maintenance_event = MaintenanceEvent.objects.filter(
                maintenancehistory=instance).order_by(
                    '-eventdatetime_standarddatetime')[0]
            event_description = last_maintenance_event.eventdescription_set.all()[0].eventdescription
            #reversion.set_user(self.request.user)
            reversion.set_comment(event_description)
        kwargs = {"record_id": self.kwargs.get("record_id")}
        url = reverse("editor:record-wizard", kwargs=kwargs) + "?saved=true"
        return redirect(url)

    def get_form_instance(self, step):
        return get_object_or_404(EAD, pk=self.kwargs.get("record_id"))

    def get_prefix(self, request, *args, **kwargs):
        # Get a prefix that includes the record ID so that data does
        # not bleed across if a user switches from editing one record
        # to another without completing the first.
        prefix = super().get_prefix(request, *args, **kwargs)
        return "{}-record-{}".format(prefix, self.kwargs.get("record_id"))

    def get_step_url(self, step):
        record_id = self.kwargs["record_id"]
        return reverse(self.url_name, kwargs={"record_id": record_id, "step": step})

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]


def entity_edit(request, entity_type, entity_id):
    if entity_type == 'corpname':
        entity_type_name = 'Corporate body'
        form_class = forms.CorpNameEditForm
        model = CorpName
    elif entity_type == 'persname':
        entity_type_name = 'Person'
        form_class = forms.PersNameEditForm
        model = PersName
    else:
        raise Http404()
    entity = get_object_or_404(model, pk=entity_id)
    # Since we are not doing anything with the name, and only editing
    # its one part, avoid the complexity of container forms and inline
    # formsets and just have the form built for the part. There's no
    # way this could cause problems later.
    part = entity.part_set.all()[0]
    form_errors = []
    if request.method == 'POST':
        form = form_class(request.POST, instance=part)
        if form.is_valid():
            form.save()
            entity.save()
            url = reverse('editor:entity-edit', kwargs={
                'entity_type': entity_type, 'entity_id': entity_id}) + \
                '?saved=true'
            return redirect(url)
        else:
            form_errors = forms.assemble_form_errors(form)
    else:
        form = form_class(instance=part)
    context = {
        'entity': entity,
        'entity_type': entity_type_name,
        'form': form,
        'form_errors': form_errors,
        'reverted': request.GET.get('reverted', False),
        'saved': request.GET.get('saved', False),
    }
    return render(request, 'editor/entity_edit.html', context)


def revert(request):
    revision_id = request.POST.get('revision_id')
    revision = get_object_or_404(Revision, pk=revision_id)
    revision.revert(delete=True)
    return redirect(request.POST.get('redirect_url')
                    + '?reverted={}'.format(revision_id))
