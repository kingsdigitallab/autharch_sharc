from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView

from formtools.wizard.views import NamedUrlSessionWizardView

from ead.models import EAD

from . import forms


class RecordList(ListView):

    queryset = EAD.objects.all()[:10]
    context_object_name = 'records'
    template_name = 'editor/record_list.html'


class RecordWizard(NamedUrlSessionWizardView):
    """Wizard for editing EAD records."""
    form_list = [
        ('contents', forms.EADContentForm),
        ('maintenance', forms.EADMaintenanceForm),
    ]
    TEMPLATES = {
        'contents': 'editor/record_wizard_content.html',
        'maintenance': 'editor/record_wizard_maintenance.html',
    }

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        context['record'] = form.instance
        if form.is_bound and not form.is_valid():
            context['form_errors'] = forms.assemble_form_errors(form)
        context['post_data'] = self.request.POST
        return context

    def done(self, form_list, **kwargs):
        for form in form_list:
            form.save()
        kwargs = {'record_id': self.kwargs.get('record_id')}
        url = reverse('editor:record-wizard', kwargs=kwargs) + '?saved=true'
        return redirect(url)

    def get_form_instance(self, step):
        return get_object_or_404(EAD, pk=self.kwargs.get('record_id'))

    def get_prefix(self, request, *args, **kwargs):
        # Get a prefix that includes the record ID so that data does
        # not bleed across if a user switches from editing one record
        # to another without completing the first.
        prefix = super().get_prefix(request, *args, **kwargs)
        return '{}-record-{}'.format(prefix, self.kwargs.get('record_id'))

    def get_step_url(self, step):
        record_id = self.kwargs['record_id']
        return reverse(self.url_name, kwargs={'record_id': record_id,
                                              'step': step})

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]
