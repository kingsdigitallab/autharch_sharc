from django.views.generic import FormView
from django.views.generic.list import MultipleObjectMixin


class SearchView(MultipleObjectMixin, FormView):
    """Form view that handles searches via a form that is submitted via
    HTTP GET."""

    form_name = 'search_form'
    object_list = None
    search_field = 'q'

    def form_invalid(self, form):
        context = self.get_context_data(**{
            self.form_name: form,
            self.context_object_name: self.get_queryset(),
        })
        return self.render_to_response(context)

    def form_valid(self, form):
        query = form.cleaned_data.get(self.search_field)
        requested_facets = self._split_selected_facets(
            self.request.GET.getlist(self.facet_key))
        kwargs = {}
        if query:
            kwargs['query'] = query
        if requested_facets:
            kwargs['filters'] = requested_facets
        kwargs.update(self._get_filters())
        search = self.search_class(**kwargs)
        response = search.execute()
        facets, selected_facets = self._annotate_facets(
            response.facets, self.request.GET)
        context = self.get_context_data(
            **{
                self.context_object_name: response,
                self.form_name: form,
                "facets": facets,
                "query": query,
                "results_count": response.hits.total.value,
                "selected_facets": selected_facets,
            }
        )
        return self.render_to_response(context)

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = {'initial': self.get_initial()}
        if self.request.method == 'GET':
            kwargs.update({
                'data': self.request.GET,
            })
        return kwargs

    def get_queryset(self):
        return self.search_class().search()
