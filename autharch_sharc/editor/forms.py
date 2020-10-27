from django import forms

from lxml import etree

from ead.constants import NS_MAP
from ead.models import (
    Bibliography, EAD, EventDescription, MaintenanceEvent, Source, SourceEntry)


class BibRefForm(forms.Form):
    bibref = forms.CharField(widget=forms.Textarea)

    def save(self, *args, **kwargs):
        pass


class ContainerModelForm(forms.ModelForm):

    """Base class for model forms that have associated inline formsets.

    These inline formsets must be individually created and added to
    self.formsets in _add_formsets. Each must have its own prefix,
    consisting of self.prefix and something corresponding to the
    inline.

    The formsets are stored in a dictionary, to allow for reference in
    a template to a specific formset, for custom display. Note that
    general rendering of the form will *not* work, since the contained
    formsets will not render (including the management forms) and
    validation of supplied data will therefore fail.

    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formsets = self._add_formsets(*args, **kwargs)

    def _add_formsets(self, *args, **kwargs):
        raise NotImplementedError

    def has_changed(self):
        return bool(self.changed_data) or \
            any(formset.has_changed() for formset in self.formsets.values())

    def is_valid(self):
        return super().is_valid() and \
            all(formset.is_valid() for formset in self.formsets.values())

    @property
    def media(self):
        media = super().media
        for formset in self.formsets.values():
            media += formset.media
        return media

    def save(self, commit=True):
        result = super().save(commit)
        for formset in self.formsets.values():
            if isinstance(formset, forms.models.BaseModelFormSet):
                formset.save(commit)
        return result


class BibliographyInlineForm(ContainerModelForm):

    # The Bibliography model contains the mixed content in a single
    # textfield, but for this app the contents are constrained to
    # bibref elements, so create have a non-model formset for each of
    # them, and manipulate the data into and out of the model field.

    bibliography = forms.CharField(required=False)

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        initial_bibrefs = self._parse_bibliography()
        BibRefFormset = forms.formset_factory(
            BibRefForm, can_delete=True, extra=0, min_num=1, validate_min=True)
        formsets['bibrefs'] = BibRefFormset(
            data, initial=initial_bibrefs, prefix=self.prefix + '-bibref')
        return formsets

    def clean_bibliography(self):
        formset = self.formsets['bibrefs']
        bibrefs = [
            form.cleaned_data['bibref'] for form in formset.forms
            if form not in formset.deleted_forms]
        bibliography = ''.join(bibrefs)
        return bibliography

    def _parse_bibliography(self):
        """Returns the bibrefs in the instance's bibliography field as initial
        data for a non-model formset."""
        bibrefs = []
        root = etree.fromstring('<wrapper>{}</wrapper>'.format(
            self.instance.bibliography))
        for bibref in root.xpath('//e:bibref', namespaces=NS_MAP):
            bibrefs.append({'bibref': etree.tostring(
                bibref, encoding='unicode', xml_declaration=False)})
        return bibrefs

    class Meta:
        model = Bibliography
        fields = ['archdesc', 'bibliography', 'id']


class EventDescriptionInlineForm(forms.ModelForm):

    class Meta:
        model = EventDescription
        fields = ['maintenanceevent', 'eventdescription', 'id']


class MaintenanceEventInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        EventDescriptionFormset = forms.inlineformset_factory(
            MaintenanceEvent, EventDescription,
            form=EventDescriptionInlineForm, extra=0, min_num=1,
            validate_min=True)
        formsets['eventdescriptions'] = EventDescriptionFormset(
            data, instance=self.instance,
            prefix=self.prefix + '-eventdescription')
        return formsets

    class Meta:
        model = MaintenanceEvent
        fields = ['id', 'maintenancehistory', 'agent', 'agenttype_value',
                  'eventtype_value']


class SourceEntryInlineForm(forms.ModelForm):

    class Meta:
        model = SourceEntry
        fields = ['id', 'sourceentry']


class SourceInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        SourceEntryFormset = forms.inlineformset_factory(
            Source, SourceEntry, form=SourceEntryInlineForm, extra=0)
        formsets['sourceentries'] = SourceEntryFormset(
            data, instance=self.instance, prefix=self.prefix + '-sourceentry')
        return formsets

    class Meta:
        model = Source
        fields = ['id']


class EADContentForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        BibliographyFormset = forms.inlineformset_factory(
            EAD, Bibliography, form=BibliographyInlineForm, extra=0, max_num=1,
            validate_max=True)
        formsets['bibliographies'] = BibliographyFormset(
            data, instance=self.instance, prefix='bibliography')
        SourceFormset = forms.inlineformset_factory(
            EAD, Source, form=SourceInlineForm, extra=0)
        formsets['sources'] = SourceFormset(
            data, instance=self.instance, prefix='source')
        return formsets

    class Meta:
        model = EAD
        fields = ['recordid']


class EADMaintenanceForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        MaintenanceEventFormset = forms.inlineformset_factory(
            EAD, MaintenanceEvent, form=MaintenanceEventInlineForm, extra=0,
            min_num=1, validate_min=True)
        formsets['maintenanceevents'] = MaintenanceEventFormset(
            data, instance=self.instance,
            prefix='maintenanceevent')
        return formsets

    class Meta:
        model = EAD
        fields = ['maintenancestatus_value', 'publicationstatus_value']


def assemble_form_errors(form):
    """Return a dictionary of errors for `form` and any formset
    descendants it has.

    The dictionary has keys for field errors and non-field
    errors. Field errors is a Boolean indicating whether there are any
    field errors anywhere. Non-field errors are a list of error
    strings.

    """
    def add_form_errors(errors, form):
        for field, field_errors in form.errors.items():
            if field == '__all__':
                errors['non_field'].extend(field_errors)
            else:
                errors['field'] = True
        if hasattr(form, 'formsets'):
            for formset in form.formsets.values():
                for form in formset.forms:
                    errors = add_form_errors(errors, form)
        return errors

    errors = {'field': False, 'non_field': []}
    errors = add_form_errors(errors, form)
    if not(errors['field'] or errors['non_field']):
        errors = {}
    return errors
