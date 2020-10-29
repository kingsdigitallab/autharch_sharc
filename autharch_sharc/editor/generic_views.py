from django.views.generic import FormView
from django.views.generic.edit import FormMixin
from django.views.generic.list import MultipleObjectMixin


class SearchMixin(MultipleObjectMixin, FormMixin):

    form_name = 'search_form'
    object_list = None
    search_field = 'q'

    def form_invalid(self, form):
        context = self.get_context_data(**{
            self.form_name: form,
            self.context_object_name: self.get_queryset(),
        })
        return self.render_to_response(context)


class SearchView(SearchMixin, FormView):

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
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
