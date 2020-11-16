from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from ead.models import CorpName, EAD, FamName, Name, PersName
from elasticsearch_dsl import FacetedSearch, TermsFacet
from formtools.wizard.views import NamedUrlSessionWizardView

from . import forms
from .documents import EADDocument
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


class RecordSearch(FacetedSearch):
    doc_types = [EADDocument]
    facets = {
        'categories': TermsFacet(field='category'),
        'creators': TermsFacet(field='creators.key', size=10),
    }
    fields = ['creators.name', 'unittitle']


class RecordList(SearchView, FacetMixin):

    context_object_name = "records"
    form_class = forms.EADSearchForm
    search_class = RecordSearch
    template_name = "editor/record_list.html"

    def form_valid(self, form):
        query = form.cleaned_data.get(self.search_field)
        requested_facets = self._split_selected_facets(
            self.request.GET.getlist(self.facet_key))
        kwargs = {}
        if query:
            kwargs['query'] = query
        if requested_facets:
            kwargs['filters'] = requested_facets
        search = self.search_class(**kwargs)
        response = search.execute()
        facets, selected_facets = self._annotate_facets(
            response.facets, self.request.GET)
        context = self.get_context_data(
            **{
                self.context_object_name: response,
                self.form_name: form,
                'facets': facets,
                "query": query,
                'results_count': response.hits.total.value,
                'selected_facets': selected_facets,
            }
        )
        return self.render_to_response(context)


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
        context["record"] = form.instance
        if form.is_bound and not form.is_valid():
            context["form_errors"] = forms.assemble_form_errors(form)
        context["post_data"] = self.request.POST
        return context

    def done(self, form_list, **kwargs):
        for form in form_list:
            form.save()
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
