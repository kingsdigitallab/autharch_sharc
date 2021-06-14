from django.core.paginator import Page, Paginator
from django.views.generic import FormView
from django.views.generic.list import MultipleObjectMixin

from .api_views import EditorTableView


class ElasticPaginator(Paginator):
    """ Paginator that will work with elastic search"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.count = self.object_list.hits.total.value

    def page(self, number):
        number = self.validate_number(number)
        return Page(self.object_list, number, self)


class SearchView(MultipleObjectMixin, FormView):
    """Form view that handles searches via a form that is submitted via
    HTTP GET."""

    form_name = "search_form"
    object_list = None
    search_field = "q"
    perPage = 10

    def form_invalid(self, form):
        context = self.get_context_data(
            **{
                self.form_name: form,
                self.context_object_name: self.get_queryset(),
            }
        )
        return self.render_to_response(context)

    def form_valid(self, form):

        query = form.cleaned_data.get(self.search_field)
        requested_facets = self._split_selected_facets(
            self.request.GET.getlist(self.facet_key)
        )
        kwargs = {}
        if self.request.GET:
            # in table filters
            title_filter = self.request.GET.get("filter[0]")
            # category_filter = self.request.GET.get("filter[1]")
            # unit_id_filter = self.request.GET.get("filter[2]")
            # updated_filter = self.request.GET.get("filter[3]")
            if title_filter:
                kwargs["unittitle"] = title_filter

        if query:
            kwargs["query"] = query
        if requested_facets:
            kwargs["filters"] = requested_facets

        kwargs.update(self._get_filters())
        search = self.search_class(**kwargs)

        page = int(self.request.GET.get("page", "1"))
        per_page = int(self.request.GET.get("paginate_by", self.perPage))
        start = (page - 1) * per_page

        end = start + per_page

        response = search[start:end].execute()
        paginator = ElasticPaginator(response, per_page)
        page_obj = paginator.get_page(page)
        facets, selected_facets = self._annotate_facets(
            response.facets, self.request.GET
        )
        facet_link = self.create_facet_link(self.request.GET)

        context = self.get_context_data(
            **{
                self.context_object_name: response,
                self.form_name: form,
                "paginator": paginator,
                "paginate_by": per_page,
                "page_obj": page_obj,
                "facets": facets,
                "query": query,
                "results_count": response.hits.total.value,
                "selected_facets": selected_facets,
                "facet_link": facet_link,
            }
        )
        if (
            "result_format" in self.request.GET
            and self.request.GET["result_format"] == "json"
        ):
            return EditorTableView().dispatch(self.request, **context)
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = {"initial": self.get_initial()}
        if self.request.method == "GET":
            kwargs.update(
                {
                    "data": self.request.GET,
                }
            )
        return kwargs

    def get_queryset(self):
        return self.search_class().search()
