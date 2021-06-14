import reversion
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView
from ead.models import (
    EAD,
    OriginationCorpName,
    OriginationFamName,
    OriginationName,
    OriginationPersName,
    UnitDateStructuredDateRange,
)
from elasticsearch_dsl import FacetedSearch, TermsFacet
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from reversion.models import Revision, Version
from reversion.views import create_revision

from . import forms
from .documents import EADDocument
from .generic_views import SearchView
from .signals import view_post_save


def _print_error_log(form, indent=0):
    """Print debugging information about a failed form and all of its
    descendants.

    Useful when there are no error messages (as, for example,
    validate_max or validate_min on a formset fails).

    """
    for field, field_errors in form.errors.items():
        print("{}{}: {}".format(" " * indent, field, field_errors))
    if hasattr(form, "formsets"):
        for formset in form.formsets.values():
            print("{}{}: {}".format(" " * indent, type(formset), formset.is_valid()))
            non_form_errors = formset.non_form_errors()
            if non_form_errors:
                print(non_form_errors)
            for form in formset.forms:
                _print_error_log(form, indent + 2)


class FacetMixin:
    facet_key = "facets"  # GET querystring name for facet name/value pairs

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
            if facet_name == "creators":
                display_values = {
                    "corpname": OriginationCorpName,
                    "famname": OriginationFamName,
                    "name": OriginationName,
                    "persname": OriginationPersName,
                }
            for idx, (value, count, selected) in enumerate(facets[facet_name]):
                if selected:
                    link = self._create_unapply_link(facet_name, value, query_dict)
                else:
                    link = self._create_apply_link(facet_name, value, query_dict)
                if display_values is None:
                    display_value = value
                else:
                    if facet_name == "creators":
                        creator_type, pk = value.split("-")
                        display_value = (
                            display_values[creator_type]
                            .objects.get(pk=pk)
                            .assembled_name
                        )
                new_data = (display_value, count, link, selected)
                facets[facet_name][idx] = new_data
                if selected:
                    selected_facets.append(new_data)
        return facets, selected_facets

    def _create_apply_link(self, facet_name, value, query_dict):
        """Return a querystring to apply the facet `value` to the existing
        querystring in `query_dict`."""
        new_facet = "{}:{}".format(facet_name, value)
        qd = query_dict.copy()
        facets = qd.getlist(self.facet_key)
        facets.append(new_facet)
        qd.setlist(self.facet_key, facets)
        if "page" in qd:
            qd["page"] = 1
        link = "?{}".format(qd.urlencode())
        return link

    def create_facet_link(self, query_dict):
        """Return a querystring of facets for use in pagination"""
        qd = query_dict.copy()
        facets = qd.getlist(self.facet_key)
        qd.setlist(self.facet_key, facets)
        if "page" in qd:
            del qd["page"]
        if "paginate_by" in qd:
            del qd["paginate_by"]
        link = "{}".format(qd.urlencode())
        return link

    def _create_unapply_link(self, facet_name, value, query_dict):
        """Return a querystring to unapply the facet `value` from the existing
        querystring in `query_dict`."""
        old_facet = "{}:{}".format(facet_name, value)
        qd = query_dict.copy()
        facets = qd.getlist(self.facet_key)
        facets.remove(old_facet)
        qd.setlist(self.facet_key, facets)
        if "page" in qd:
            qd["page"] = 1
        link = qd.urlencode()
        if link:
            link = "?{}".format(link)
        else:
            link = "."
        return link

    def _split_selected_facets(self, selected_facets):
        """Return a dictionary of selected facet values keyed by the facet
        each belongs to."""
        split_facets = {}
        for selected_facet in selected_facets:
            facet, value = selected_facet.split(":", maxsplit=1)
            split_facets.setdefault(facet, []).append(value)
        return split_facets


class RecordDeletedListView(LoginRequiredMixin, ListView):
    template_name = "editor/record_deleted_list.html"

    def get_queryset(self):
        return EAD.objects.filter(maintenancestatus_value="deleted")


class RecordHistory(LoginRequiredMixin, DetailView):
    model = EAD
    template_name = "editor/record_history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_section"] = "records"
        context["edit_url"] = reverse(
            "editor:record-edit", kwargs={"record_id": self.object.pk}
        )
        context["versions"] = Version.objects.get_for_object(self.object)
        return context


class RecordSearch(FacetedSearch):
    index = "editor"
    doc_types = [EADDocument]
    facets = {
        # size sets the maximum number of facet values to return; ES
        # has an (overridable) limit of 250.
        "acquirers": TermsFacet(field="related_people.acquirers", size=250),
        "categories": TermsFacet(field="category", size=250),
        "performances": TermsFacet(field="related_sources.performances", size=250),
        "sources": TermsFacet(field="related_sources.sources", size=250),
        "texts": TermsFacet(field="related_sources.texts", size=250),
        "works": TermsFacet(field="related_sources.works", size=250),
    }
    fields = [
        "creators.name",
        "unittitle",
        "unittitle.raw",
        "provenance",
        "notes.raw",
        "references_published.raw",
        "references_unpublished.raw",
        "medium",
        "label",
        "reference",
        "category",
    ]

    def __init__(
        self,
        query=None,
        filters={},
        sort=(),
        creation_start=None,
        creation_end=None,
        acquisition_start=None,
        acquisition_end=None,
        reference=None,
        unittitle=None,
    ):
        self._creation_start = creation_start
        self._creation_end = creation_end
        self._acquisition_start = acquisition_start
        self._acquisition_end = acquisition_end
        self.reference = reference
        self.unittitle = unittitle
        super().__init__(query, filters, sort)

    def search(self):
        s = super().search()
        creation = {}
        if self._creation_start:
            creation["gte"] = self._creation_start
        if self._creation_end:
            creation["lte"] = self._creation_end
        if creation:
            s = s.filter("range", date_of_creation=creation)
        acquisition = {}
        if self._acquisition_start:
            acquisition["gte"] = self._acquisition_start
        if self._acquisition_end:
            acquisition["lte"] = self._acquisition_end
        if acquisition:
            s = s.filter("range", date_of_acquisition=acquisition)
        if self.reference:
            try:
                s = s.filter("match", reference=self.reference)
            except TypeError:
                pass
        if self.unittitle:
            s = s.query("prefix", unittitle__raw=self.unittitle)
        return s


class RecordList(LoginRequiredMixin, SearchView, FacetMixin):
    context_object_name = "records"
    form_class = forms.EADRecordSearchForm
    search_class = RecordSearch
    template_name = "editor/record_list.html"

    def _create_unapply_year_link(self, query_dict, prefix):
        """Return a query string to unapply the start and end year 'facet' for
        the `prefix` range."""
        qd = query_dict.copy()
        start = prefix + "_start_year"
        end = prefix + "_end_year"
        qd.pop(start, None)
        qd.pop(end, None)
        link = qd.urlencode()
        if link:
            link = "?{}".format(link)
        else:
            link = "."
        return link

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_queryset()
        context["acquisition_max_year"] = context["form"]._acquisition_max_year
        context["acquisition_min_year"] = context["form"]._acquisition_min_year
        context["acquisition_end_year"] = self.request.GET.get("acquisition_end_year")
        context["acquisition_start_year"] = self.request.GET.get(
            "acquisition_start_year"
        )
        context["acquisition_year_remove_link"] = self._create_unapply_year_link(
            self.request.GET, "acquisition"
        )
        context["creation_max_year"] = context["form"]._creation_max_year
        context["creation_min_year"] = context["form"]._creation_min_year
        context["creation_end_year"] = self.request.GET.get("creation_end_year")
        context["creation_start_year"] = self.request.GET.get("creation_start_year")
        context["creation_year_remove_link"] = self._create_unapply_year_link(
            self.request.GET, "creation"
        )
        context["current_section"] = "records"
        return context

    def _get_date_range(self, datechar):
        dates = (
            UnitDateStructuredDateRange.objects.exclude(fromdate_standarddate="")
            .filter(parent__datechar=datechar)
            .values_list("fromdate_standarddate", "todate_standarddate")
        )
        if len(dates) == 0:
            return None, None
        start_dates = []
        end_dates = []
        for date in dates:
            start_dates.append(date[0][:4])
            end_dates.append(date[1][:4])
        if not end_dates:
            end_dates = start_dates
        min_year = sorted(start_dates)[0]
        max_year = sorted(end_dates, reverse=True)[0]
        return min_year, max_year

    def _get_filters(self):
        """Return a dictionary containing any filters to apply to the search
        results before facetting.

        These extra filters must be explicitly accommodated by the
        search_class implementation.

        """
        qs = self.request.GET
        filters = {
            "acquisition_start": qs.get("acquisition_start_year"),
            "acquisition_end": qs.get("acquisition_end_year"),
            "creation_start": qs.get("creation_start_year"),
            "creation_end": qs.get("creation_end_year"),
            "reference": qs.get("reference"),
        }
        for key in list(filters.keys()):
            if filters[key] is None:
                del filters[key]
        return filters

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        acquisition_min_year, acquisition_max_year = self._get_date_range("acquisition")
        creation_min_year, creation_max_year = self._get_date_range("creation")
        kwargs.update(
            {
                "acquisition_max_year": acquisition_max_year,
                "acquisition_min_year": acquisition_min_year,
                "creation_max_year": creation_max_year,
                "creation_min_year": creation_min_year,
            }
        )
        return kwargs


class RecordListApiView(APIView):
    """Extra view to return table data as an api call """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def document_search(self, request, **kwargs):
        # pass request to record list
        kwargs = {"request": request}
        record_list = RecordList(**kwargs)
        context = record_list.get_context_data(**kwargs)
        if "results_count" in context:
            results_count = context["results_count"]
        else:
            results_count = 0
        if "object_list" in context:
            object_list = context["object_list"]
        else:
            object_list = []
        # record_list.context_object_name
        #
        return {"count": results_count, "results": object_list}

    def get(self, request, *args, **kwargs):
        results = self.document_search(request, **kwargs)
        return Response({"data": results})


@login_required
def home(request):
    return redirect(reverse("editor:record-list"))


@login_required
def record_create(request):
    form_errors = []
    if request.method == "POST":
        form = forms.RecordEditForm(request.POST)
        if form.is_valid():
            with reversion.create_revision():
                record = form.save()
                reversion.set_comment("Created")
            view_post_save.send(sender=EAD, instance=record)
            url = (
                reverse("editor:record-edit", kwargs={"record_id": record.pk})
                + "?saved=true"
            )
            return redirect(url)
        else:
            form_errors = forms.assemble_form_errors(form)
    else:
        form = forms.RecordEditForm()
    context = {
        "current_section": "records",
        "form": form,
        "form_media": form.media,
        "form_errors": form_errors,
        "reverted": request.GET.get("reverted", False),
        "saved": request.GET.get("saved", False),
    }
    return render(request, "editor/record_edit.html", context)


@login_required
@create_revision()
@require_POST
def record_delete(request, record_id):
    record = get_object_or_404(EAD, pk=record_id)
    if is_deleted_record(record):
        return redirect("editor:record-history", record_id=record_id)
    if request.POST.get("DELETE") == "DELETE":
        reversion.set_comment("Deleted")
        reversion.set_user(request.user)
        record.maintenancestatus_value = "deleted"
        record.save()
        view_post_save.send(sender=EAD, instance=record)
        return redirect("editor:record-list")
    return redirect("editor:record-edit", record_id=record_id)


@login_required
def record_edit(request, record_id):
    record = get_object_or_404(EAD, pk=record_id)
    form_errors = []
    is_deleted = is_deleted_record(record)
    if is_deleted:
        current_section = "deleted"
    else:
        current_section = "records"
    if request.method == "POST":
        form = forms.RecordEditForm(request.POST, instance=record)
        if form.is_valid():
            # The maintenance status is always revised after an edit;
            # this resets it if the record is being restored after
            # deletion.
            record.maintenancestatus_value = "revised"
            with reversion.create_revision():
                form.save()
                reversion.set_user(request.user)
                reversion.set_comment("Edited")
            view_post_save.send(sender=EAD, instance=record)
            url = (
                reverse("editor:record-edit", kwargs={"record_id": record_id})
                + "?saved=true"
            )
            return redirect(url)
        else:
            form_errors = forms.assemble_form_errors(form)
    else:
        form = forms.RecordEditForm(instance=record)
    context = {
        "current_section": current_section,
        "delete_url": reverse("editor:record-delete", kwargs={"record_id": record_id}),
        "form": form,
        "form_media": form.media,
        "form_errors": form_errors,
        "is_deleted": is_deleted,
        "record": record,
        "reverted": request.GET.get("reverted", False),
        "saved": request.GET.get("saved", False),
    }
    return render(request, "editor/record_edit.html", context)


@login_required
def revert(request):
    revision_id = request.POST.get("revision_id")
    revision = get_object_or_404(Revision, pk=revision_id)
    revision.revert(delete=True)
    return redirect(
        request.POST.get("redirect_url") + "?reverted={}".format(revision_id)
    )


def is_deleted_record(record):
    return record.maintenancestatus_value == "deleted"
