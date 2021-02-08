from django import forms

from lxml import etree

from controlled_vocabulary.models import ControlledTerm
from ead.constants import EAD_NAMESPACE, EAD_NS, NS_MAP
from ead.models import (
    Bibliography, ControlAccess, CustodHist, DIdPhysDescStructured,
    DIdPhysDescStructuredDimensions, DIdPhysDescStructuredPhysFacet, EAD,
    EventDescription, LanguageDeclaration, MaintenanceEvent, Origination,
    OriginationCorpName, OriginationCorpNamePart, OriginationPersName,
    OriginationPersNamePart, PhysLoc, RelatedMaterial, Relation, RelationEntry,
    RightsDeclaration, ScopeContent, Source, SourceEntry, UnitDate,
    UnitDateStructured, UnitDateStructuredDateRange, UnitTitle)


NS_MAP_2 = {None: EAD_NAMESPACE}


ENTITY_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search all people and corporate bodies',
    'type': 'search',
}

RECORD_SEARCH_INPUT_ATTRS = {
    'aria-label': 'Search',
    'placeholder': 'Search all archival records',
    'type': 'search',
}

RECORD_SEARCH_START_YEAR_INPUT_ATTRS = {
    'aria-label': 'Start year',
}

RECORD_SEARCH_END_YEAR_INPUT_ATTRS = {
    'aria-label': 'End year',
}


def serialise_xml(element, method='xml'):
    return etree.tostring(element, encoding='unicode', method=method,
                          xml_declaration=False)


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


class ArchRefInlineForm(forms.Form):

    archref = forms.CharField(label='Related entry', required=False,
                              widget=forms.Textarea)

    def clean_archref(self):
        item = etree.Element(EAD_NS + 'archref', nsmap=NS_MAP_2)
        item.text = self.cleaned_data['archref']
        return item


class BibliographyInlineForm(forms.ModelForm):

    # The Bibliography model contains the mixed content in a single
    # textfield, but for this app the contents are constrained to
    # bibref elements, so create have a non-model formset for each of
    # them, and manipulate the data into and out of the model field.

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            kwargs.update(initial={'bibliography': self._parse_bibliography(
                instance)})
        super().__init__(*args, **kwargs)

    def clean_bibliography(self):
        bibrefs = []
        data = self.cleaned_data['bibliography'].replace('\r\n', '\n').replace(
            '\r', '\n')
        for text in data.split('\n\n'):
            bibref = etree.Element(EAD_NS + 'bibref', nsmap=NS_MAP_2)
            bibref.text = text
            bibrefs.append(serialise_xml(bibref))
        return ''.join(bibrefs)

    def _parse_bibliography(self, instance):
        """Returns the bibrefs in the instance's bibliography field as initial
        data for a non-model formset."""
        bibrefs = []
        root = etree.fromstring('<wrapper>{}</wrapper>'.format(
            instance.bibliography))
        for bibref in root.xpath('//e:bibref', namespaces=NS_MAP):
            bibrefs.append(serialise_xml(bibref, method='text'))
        return '\n\n'.join(bibrefs)

    class Meta:
        model = Bibliography
        fields = ['bibliography', 'id']
        labels = {
            'bibliography': 'Published references',
        }


class ControlAccessInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        initial_genreforms, initial_geognames, initial_persnames = \
            self._parse_controlaccess()
        GenreformFormset = forms.formset_factory(
            GenreformInlineForm, can_delete=True, extra=1, max_num=1,
            validate_max=True)
        formsets['genreforms'] = GenreformFormset(
            data, initial=initial_genreforms,
            prefix=self.prefix + '-genreform')
        GeognameFormset = forms.formset_factory(
            GeognameInlineForm, can_delete=True, extra=1, max_num=1,
            validate_max=True)
        formsets['geognames'] = GeognameFormset(
            data, initial=initial_geognames, prefix=self.prefix + '-geogname')
        PersnameFormset = forms.formset_factory(
            PersnameNonModelInlineForm, can_delete=True, extra=0)
        formsets['persnames'] = PersnameFormset(
            data, initial=initial_persnames, prefix=self.prefix + '-persname')
        return formsets

    def clean_controlaccess(self):
        controlaccess = []
        subs = [('genreforms', 'genreform'), ('geognames', 'geogname'),
                ('persnames', 'persname')]
        for formset_name, field_name in subs:
            formset = self.formsets[formset_name]
            controlaccess.extend(
                [form.cleaned_data.get(field_name, '')
                 for form in formset.forms
                 if form not in formset.deleted_forms])
        return ''.join(controlaccess)

    def _parse_controlaccess(self):
        """Returns the genreforms, geognames, and persnames in the instance's
        controlaccess field as initial data for non-model formsets."""
        root = etree.fromstring('<wrapper>{}</wrapper>'.format(
            self.instance.controlaccess))
        genreforms = [{'genreform': serialise_xml(genreform, method='text')}
                      for genreform in root.xpath('//e:genreform',
                                                  namespaces=NS_MAP)]
        geognames = [{'geogname': serialise_xml(geogname, method='text')}
                     for geogname in root.xpath('//e:geogname',
                                                namespaces=NS_MAP)]
        persnames = [{
            'persname': serialise_xml(persname, method='text'),
            'relator': persname.get('relator', '')}
                     for persname in root.xpath('//e:persname',
                                                namespaces=NS_MAP)]
        return genreforms, geognames, persnames

    class Meta:
        model = ControlAccess
        fields = ['controlaccess', 'id']
        widgets = {
            'controlaccess': forms.HiddenInput(),
        }


class CustodHistInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            xml = etree.fromstring('<wrapper>{}</wrapper>'.format(
                instance.custodhist))
            texts = []
            for para in xml.xpath('//e:p', namespaces=NS_MAP):
                texts.append(serialise_xml(para, method='text'))
            kwargs.update(initial={'custodhist': '\n\n'.join(texts)})
        super().__init__(*args, **kwargs)

    def clean_custodhist(self):
        # Convert consecutive newlines into paragraph breaks.
        paras = []
        data = self.cleaned_data['custodhist'].replace('\r\n', '\n').replace(
            '\r', '\n')
        for para in data.split('\n\n'):
            p = etree.Element(EAD_NS + 'p', nsmap=NS_MAP_2)
            p.text = para
            paras.append(serialise_xml(p))
        return ''.join(paras)

    class Meta:
        model = CustodHist
        fields = ['id', 'custodhist']
        labels = {
            'custodhist': 'Provenance'
        }


class EventDescriptionInlineForm(forms.ModelForm):

    class Meta:
        model = EventDescription
        fields = ['maintenanceevent', 'eventdescription', 'id']


class GenreformInlineForm(forms.Form):

    genreform = forms.CharField()

    def clean_genreform(self):
        item = etree.Element(EAD_NS + 'genreform', nsmap=NS_MAP_2)
        item.set('source', 'AAT')
        item.text = self.cleaned_data['genreform']
        return serialise_xml(item)


class GeognameInlineForm(forms.Form):

    geogname = forms.CharField(label='Place of origin')

    def clean_geogname(self):
        item = etree.Element(EAD_NS + 'geogname', nsmap=NS_MAP_2)
        part = etree.SubElement(item, EAD_NS + 'part', nsmap=NS_MAP_2)
        part.text = self.cleaned_data['geogname']
        return serialise_xml(item)


class LabelInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        PhysFacetFormset = forms.inlineformset_factory(
            DIdPhysDescStructured, DIdPhysDescStructuredPhysFacet,
            form=LabelPhysFacetInlineForm, extra=1, max_num=1, min_num=1,
            validate_max=True, validate_min=True)
        formsets['physfacets'] = PhysFacetFormset(
            data, instance=self.instance, prefix=self.prefix + '-physfacet')
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.physdescstructuredtype = DIdPhysDescStructured.STRUCTURED_TYPE_OTHER
            self.instance.otherphysdescstructuredtype = 'label_inscription_caption'
            self.instance.quantity = 1
            self.instance.unittype = 'item'
            self.instance.coverage = DIdPhysDescStructured.COVERAGE_PART
        super().save(commit)

    class Meta:
        model = DIdPhysDescStructured
        fields = ['id']


class LabelPhysFacetInlineForm(forms.ModelForm):

    class Meta:
        model = DIdPhysDescStructuredPhysFacet
        fields = ['id', 'physfacet']
        labels = {
            'physfacet': 'Label/inscription/caption',
        }


class LanguageDeclarationInlineForm(forms.ModelForm):

    def clean(self):
        # Set the language from the language code.
        cleaned_data = super().clean()
        lang_term = cleaned_data.get('language_langcode')
        cleaned_data['language'] = lang_term.label
        return cleaned_data

    class Meta:
        model = LanguageDeclaration
        fields = ['id', 'language', 'language_langcode', 'script_el_script']
        labels = {
            'language_langcode': 'Record language',
            'script_el_script': 'Record script',
        }
        widgets = {
            'language': forms.HiddenInput(),
        }


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


class MediumInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        PhysFacetFormset = forms.inlineformset_factory(
            DIdPhysDescStructured, DIdPhysDescStructuredPhysFacet,
            form=MediumPhysFacetInlineForm, extra=1, max_num=1, min_num=1,
            validate_max=True, validate_min=True)
        formsets['physfacets'] = PhysFacetFormset(
            data, instance=self.instance, prefix=self.prefix + '-physfacet')
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.physdescstructuredtype = DIdPhysDescStructured.STRUCTURED_TYPE_MATERIAL
            self.instance.quantity = 1
            self.instance.unittype = 'item'
            self.instance.coverage = DIdPhysDescStructured.COVERAGE_WHOLE
        super().save(commit)

    class Meta:
        model = DIdPhysDescStructured
        fields = ['id']


class MediumPhysFacetInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            xml = etree.fromstring('<wrapper>{}</wrapper>'.format(
                instance.physfacet))
            try:
                part = xml.xpath('e:genreform[1]/e:part[1]',
                                 namespaces=NS_MAP)[0]
                text = serialise_xml(part, method='text')
            except IndexError:
                text = ''
            kwargs.update(initial={'physfacet': text})
        super().__init__(*args, **kwargs)

    def clean_physfacet(self):
        genreform = etree.Element(EAD_NS + 'genreform', nsmap=NS_MAP_2)
        part = etree.SubElement(genreform, EAD_NS + 'part', nsmap=NS_MAP_2)
        part.text = self.cleaned_data['physfacet']
        return serialise_xml(genreform)

    class Meta:
        model = DIdPhysDescStructuredPhysFacet
        fields = ['id', 'physfacet']
        labels = {
            'physfacet': 'Medium',
        }


class OriginationInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        PersNameFormset = forms.inlineformset_factory(
            Origination, OriginationPersName, exclude=[],
            form=OriginationPersNameInlineForm, extra=1, max_num=1, min_num=1,
            validate_max=True, validate_min=True)
        formsets['persnames'] = PersNameFormset(
            data, instance=self.instance, prefix=self.prefix + '-persname')
        return formsets

    class Meta:
        model = Origination
        fields = ['id', 'label']


class OriginationPersNameInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        PartFormset = forms.inlineformset_factory(
            OriginationPersName, OriginationPersNamePart, exclude=[],
            form=OriginationPersNamePartInlineForm, extra=1, max_num=1,
            min_num=1, validate_max=True, validate_min=True)
        formsets['parts'] = PartFormset(
            data, instance=self.instance, prefix=self.prefix + '-part')
        return formsets

    class Meta:
        model = OriginationPersName
        fields = ['id']


class OriginationPersNamePartInlineForm(forms.ModelForm):

    order = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def clean_order(self):
        order = self.cleaned_data.get('order', 1) or 1
        return order

    class Meta:
        model = OriginationPersNamePart
        fields = ['id', 'order', 'part']
        labels = {
            'part': 'Creator',
        }
        widgets = {
            'part': forms.TextInput(),
        }


class PersnameNonModelInlineForm(forms.Form):

    persname = forms.CharField(label='Name')
    relator = forms.CharField(label='Association')

    def clean(self):
        cleaned_data = super().clean()
        persname = cleaned_data.get('persname')
        relator = cleaned_data.get('relator')
        if persname is not None and relator:
            persname.set('relator', relator)
        cleaned_data['persname'] = serialise_xml(persname)
        return cleaned_data

    def clean_persname(self):
        item = etree.Element(EAD_NS + 'persname', nsmap=NS_MAP_2)
        part = etree.SubElement(item, EAD_NS + 'part', nsmap=NS_MAP_2)
        part.text = self.cleaned_data['persname']
        return item


class PhyslocInlineForm(forms.ModelForm):

    class Meta:
        model = PhysLoc
        fields = ['id', 'physloc']
        labels = {
            'physloc': 'Physical location',
        }


class RelationEntryInlineForm(forms.ModelForm):

    class Meta:
        model = RelationEntry
        fields = ['id', 'localtype', 'relationentry']
        widgets = {
            'localtype': forms.HiddenInput(),
            'relationentry': forms.TextInput(),
        }


class ConnectionTypeInlineForm(RelationEntryInlineForm):

    def clean_localtype(self):
        return 'sh_connection_type'

    class Meta(RelationEntryInlineForm.Meta):
        labels = {
            'relationentry': 'Individual or works?',
        }


class PrimaryConnectionInlineForm(RelationEntryInlineForm):

    def clean_localtype(self):
        return 'work_connection_primary'

    class Meta(RelationEntryInlineForm.Meta):
        labels = {
            'relationentry': 'How does it relate to the relevant work?',
        }


class SecondaryConnectionInlineForm(RelationEntryInlineForm):

    def clean_localtype(self):
        return 'work_connection_secondary'

    class Meta(RelationEntryInlineForm.Meta):
        labels = {
            'relationentry': 'Secondary connection to relevant work?',
        }


class RelatedMaterialInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        initial_archrefs = self._parse_relatedmaterial()
        ArchRefFormset = forms.formset_factory(
            ArchRefInlineForm, can_delete=True, extra=0, min_num=1)
        formsets['archrefs'] = ArchRefFormset(
            data, initial=initial_archrefs, prefix=self.prefix + '-archref')
        return formsets

    def clean_relatedmaterial(self):
        # Wrap the archrefs in a relatedmaterial, per pcaton's instructions.
        relatedmaterial = etree.Element('relatedmaterial', nsmap=NS_MAP_2)
        formset = self.formsets['archrefs']
        for form in formset:
            if form not in formset.deleted_forms:
                archref = form.cleaned_data.get('archref')
                if archref is not None:
                    relatedmaterial.append(archref)
        return serialise_xml(relatedmaterial)

    def _parse_relatedmaterial(self):
        """Returns the archref descendants in the instance's relatedmaterial
        field as initial data for non-model formsets."""
        root = etree.fromstring('<wrapper>{}</wrapper>'.format(
            self.instance.relatedmaterial))
        archrefs = [{'archref': serialise_xml(archref, method='text')}
                    for archref in root.xpath('//e:archref',
                                              namespaces=NS_MAP)]
        return archrefs

    class Meta:
        model = RelatedMaterial
        fields = ['id', 'relatedmaterial']
        widgets = {
            'relatedmaterial': forms.HiddenInput(),
        }


class RelationInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        ConnectionTypeFormset = forms.inlineformset_factory(
            Relation, RelationEntry, form=ConnectionTypeInlineForm, extra=1,
            max_num=1, min_num=1, validate_max=True, validate_min=True)
        formsets['connectiontypes'] = ConnectionTypeFormset(
            data, instance=self.instance, prefix=self.prefix + '-type',
            queryset=RelationEntry.objects.filter(
                localtype='sh_connection_type'))
        PrimaryConnectionFormset = forms.inlineformset_factory(
            Relation, RelationEntry, form=PrimaryConnectionInlineForm, extra=1,
            max_num=1, min_num=1, validate_max=True, validate_min=True)
        formsets['primaryconnections'] = PrimaryConnectionFormset(
            data, instance=self.instance, prefix=self.prefix + '-primary',
            queryset=RelationEntry.objects.filter(
                localtype='work_connection_primary'))
        SecondaryConnectionFormset = forms.inlineformset_factory(
            Relation, RelationEntry, form=SecondaryConnectionInlineForm,
            extra=1, max_num=1, min_num=1, validate_max=True,
            validate_min=True)
        formsets['secondaryconnections'] = SecondaryConnectionFormset(
            data, instance=self.instance, prefix=self.prefix + '-secondary',
            queryset=RelationEntry.objects.filter(
                localtype='work_connection_secondary'))
        return formsets

    class Meta:
        model = Relation
        fields = ['id']


class RightsDeclarationInlineForm(forms.ModelForm):

    disabled_fields = ['abbr', 'citation']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    class Meta:
        model = RightsDeclaration
        fields = ['id', 'abbr', 'citation', 'descriptivenote']
        labels = {
            'abbr': 'Rights declaration abbreviation',
            'citation': 'Rights declaration citation',
            'descriptivenote': 'Rights declaration',
        }
        widgets = {
            'citation': forms.TextInput(),
        }


class ScopeContentNotesInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            xml = etree.fromstring('<wrapper>{}</wrapper>'.format(
                instance.scopecontent))
            texts = []
            for para in xml.xpath('//e:p', namespaces=NS_MAP):
                texts.append(serialise_xml(para, method='text'))
            kwargs.update(initial={'scopecontent': '\n\n'.join(texts)})
        super().__init__(*args, **kwargs)

    def clean_scopecontent(self):
        # Convert consecutive newlines into paragraph breaks.
        paras = []
        data = self.cleaned_data['scopecontent'].replace('\r\n', '\n').replace(
            '\r', '\n')
        for para in data.split('\n\n'):
            p = etree.Element(EAD_NS + 'p', nsmap=NS_MAP_2)
            p.text = para
            paras.append(serialise_xml(p))
        return ''.join(paras)

    class Meta:
        model = ScopeContent
        fields = ['id', 'scopecontent']
        labels = {
            'scopecontent': 'Notes',
        }


class ScopeContentPublicationDetailsInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is not None:
            xml = etree.fromstring('<wrapper>{}</wrapper>'.format(
                instance.scopecontent))
            kwargs.update(initial={
                'scopecontent': serialise_xml(xml, method='text')})
        super().__init__(*args, **kwargs)

    def clean_scopecontent(self):
        item = etree.Element(EAD_NS + 'p', nsmap=NS_MAP_2)
        item.text = self.cleaned_data['scopecontent']
        return serialise_xml(item)

    class Meta:
        model = ScopeContent
        fields = ['id', 'scopecontent']
        labels = {
            'scopecontent': 'Publication details',
        }


class SizeDimensionsInlineForm(forms.ModelForm):

    class Meta:
        model = DIdPhysDescStructuredDimensions
        fields = ['id', 'dimensions']
        labels = {
            'dimensions': 'Size',
        }


class SizeInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        DimensionsFormset = forms.inlineformset_factory(
            DIdPhysDescStructured, DIdPhysDescStructuredDimensions,
            form=SizeDimensionsInlineForm, extra=1, max_num=1, min_num=1,
            validate_max=True, validate_min=True)
        formsets['dimensions'] = DimensionsFormset(
            data, instance=self.instance, prefix=self.prefix + '-dimensions')
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.physdescstructuredtype = DIdPhysDescStructured.STRUCTURED_TYPE_SPACE
            self.instance.quantity = 1
            self.instance.unittype = 'item'
            self.instance.coverage = DIdPhysDescStructured.COVERAGE_WHOLE
        super().save(commit)

    class Meta:
        model = DIdPhysDescStructured
        fields = ['id']


class SourceEntryInlineForm(forms.ModelForm):

    class Meta:
        model = SourceEntry
        fields = ['id', 'sourceentry']
        labels = {
            'sourceentry': 'Unpublished reference',
        }


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


class UnitDateInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        datechar = self.instance.datechar
        if datechar == 'creation':
            self.fields['unitdate'].label = 'Date of creation notes'
        elif datechar == 'acquisition':
            self.fields['unitdate'].label = 'Date of acquisition notes'

    class Meta:
        model = UnitDate
        fields = ['unitdate']


class UnitDateStructuredDateRangeInlineForm(forms.ModelForm):

    class Meta:
        model = UnitDateStructuredDateRange
        fields = ['id', 'fromdate_standarddate', 'todate_standarddate']


class UnitDateStructuredInlineForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get('data')
        DateRangeFormset = forms.inlineformset_factory(
            UnitDateStructured, UnitDateStructuredDateRange,
            form=UnitDateStructuredDateRangeInlineForm, extra=1, max_num=1,
            validate_max=True)
        formsets['dateranges'] = DateRangeFormset(
            data, instance=self.instance, prefix=self.prefix + '-daterange')
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.datechar = 'creation'
        super().save(commit)

    class Meta:
        model = UnitDateStructured
        fields = ['id']


class UnitTitleInlineForm(forms.ModelForm):

    class Meta:
        model = UnitTitle
        fields = ['id', 'unittitle']


class RecordEditForm(ContainerModelForm):

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        BibliographyFormset = forms.inlineformset_factory(
            EAD, Bibliography, form=BibliographyInlineForm, extra=1, max_num=1,
            validate_max=True)
        formsets['bibliographies'] = BibliographyFormset(
            *args, instance=self.instance, prefix='bibliography')
        ControlAccessFormset = forms.inlineformset_factory(
            EAD, ControlAccess, form=ControlAccessInlineForm, extra=0,
            max_num=1, validate_max=True)
        formsets['controlaccesses'] = ControlAccessFormset(
            *args, instance=self.instance, prefix='controlaccess')
        CustodHistFormset = forms.inlineformset_factory(
            EAD, CustodHist, form=CustodHistInlineForm, extra=1, max_num=1,
            validate_max=True)
        formsets['custodhists'] = CustodHistFormset(
            *args, instance=self.instance, prefix='custodhist')
        LabelFormset = forms.inlineformset_factory(
            EAD, DIdPhysDescStructured, form=LabelInlineForm, extra=0,
            max_num=1, validate_max=True)
        formsets['labels'] = LabelFormset(
            *args, instance=self.instance, prefix='label',
            queryset=DIdPhysDescStructured.objects.filter(
                otherphysdescstructuredtype='label_inscription_caption'))
        MediumFormset = forms.inlineformset_factory(
            EAD, DIdPhysDescStructured, form=MediumInlineForm, extra=0,
            max_num=1, min_num=1)
        formsets['media'] = MediumFormset(
            *args, instance=self.instance, prefix='medium',
            queryset=DIdPhysDescStructured.objects.filter(
                physdescstructuredtype=DIdPhysDescStructured.STRUCTURED_TYPE_MATERIAL))
        ScopeContentNotesFormset = forms.inlineformset_factory(
            EAD, ScopeContent, form=ScopeContentNotesInlineForm, extra=1,
            max_num=1, validate_max=True)
        formsets['notes'] = ScopeContentNotesFormset(
            *args, instance=self.instance, prefix='scopecontent_notes',
            queryset=ScopeContent.objects.filter(localtype='notes'))
        OriginationFormset = forms.inlineformset_factory(
            EAD, Origination, form=OriginationInlineForm, extra=0)
        formsets['originations'] = OriginationFormset(
            *args, instance=self.instance, prefix='origination')
        PhysLocFormset = forms.inlineformset_factory(
            EAD, PhysLoc, form=PhyslocInlineForm, extra=1, max_num=1,
            validate_max=True)
        formsets['physlocs'] = PhysLocFormset(
            *args, instance=self.instance, prefix='physloc')
        ScopeContentPublicationFormset = forms.inlineformset_factory(
            EAD, ScopeContent, form=ScopeContentPublicationDetailsInlineForm,
            extra=1, max_num=1, validate_max=True)
        formsets['publication_details'] = ScopeContentPublicationFormset(
            *args, instance=self.instance,
            prefix='scopecontent_publication_details',
            queryset=ScopeContent.objects.filter(
                localtype='publication_details'))
        SizeFormset = forms.inlineformset_factory(
            EAD, DIdPhysDescStructured, form=SizeInlineForm, extra=0)
        formsets['sizes'] = SizeFormset(
            *args, instance=self.instance, prefix='size',
            queryset=DIdPhysDescStructured.objects.filter(
                physdescstructuredtype=DIdPhysDescStructured.STRUCTURED_TYPE_SPACE))
        SourceFormset = forms.inlineformset_factory(
            EAD, Source, form=SourceInlineForm, extra=0)
        formsets['sources'] = SourceFormset(
            *args, instance=self.instance, prefix='source')
        CreationDateFormset = forms.inlineformset_factory(
            EAD, UnitDateStructured, form=UnitDateStructuredInlineForm,
            extra=1, max_num=1, validate_max=True)
        formsets['creation_dates'] = CreationDateFormset(
            *args, instance=self.instance, prefix='creation_date',
            queryset=UnitDateStructured.objects.filter(datechar='creation'))
        CreationDateNoteFormset = forms.inlineformset_factory(
            EAD, UnitDate, form=UnitDateInlineForm, extra=1, max_num=1,
            validate_max=True)
        formsets['creation_date_notes'] = CreationDateNoteFormset(
            *args, instance=self.instance, prefix='creation_date_note',
            queryset=UnitDate.objects.filter(datechar='creation'))
        AcquisitionDateFormset = forms.inlineformset_factory(
            EAD, UnitDateStructured, form=UnitDateStructuredInlineForm,
            extra=1, max_num=1, validate_max=True)
        formsets['acquisition_dates'] = AcquisitionDateFormset(
            *args, instance=self.instance, prefix='acquisition_date',
            queryset=UnitDateStructured.objects.filter(datechar='acquisition'))
        AcquisitionDateNoteFormset = forms.inlineformset_factory(
            EAD, UnitDate, form=UnitDateInlineForm, extra=1, max_num=1,
            validate_max=True)
        formsets['acquisition_date_notes'] = AcquisitionDateNoteFormset(
            *args, instance=self.instance, prefix='acquisition_date_note',
            queryset=UnitDate.objects.filter(datechar='acquisition'))
        UnitTitleFormset = forms.inlineformset_factory(
            EAD, UnitTitle, form=UnitTitleInlineForm, extra=1, max_num=1,
            min_num=1, validate_max=True, validate_min=True)
        formsets['unittitles'] = UnitTitleFormset(
            *args, instance=self.instance, prefix='unittitle')
        RelationFormset = forms.inlineformset_factory(
            EAD, Relation, form=RelationInlineForm, extra=0)
        formsets['relations'] = RelationFormset(
            *args, instance=self.instance, prefix='relation',
            queryset=Relation.objects.filter(
                otherrelationtype='sh_connection'))
        RelatedMaterialFormset = forms.inlineformset_factory(
            EAD, RelatedMaterial, form=RelatedMaterialInlineForm,
            extra=1, max_num=1, validate_max=True)
        formsets['relatedmaterials'] = RelatedMaterialFormset(
            *args, instance=self.instance, prefix='relatedmaterial')
        LanguageDeclarationFormset = forms.inlineformset_factory(
            EAD, LanguageDeclaration, form=LanguageDeclarationInlineForm,
            extra=1, max_num=1, min_num=1, validate_max=True,
            validate_min=True)
        formsets['languagedeclarations'] = LanguageDeclarationFormset(
            *args, instance=self.instance, prefix='languagedeclaration')
        RightsDeclarationFormset = forms.inlineformset_factory(
            EAD, RightsDeclaration, form=RightsDeclarationInlineForm, extra=1,
            max_num=1, min_num=1, validate_max=True, validate_min=True)
        formsets['rightsdeclarations'] = RightsDeclarationFormset(
            *args, instance=self.instance, prefix='rightsdeclaration')
        return formsets

    class Meta:
        model = EAD
        fields = ['recordid']


class EADEntitySearchForm(forms.Form):

    q = forms.CharField(required=False, label="Search",
                        widget=forms.TextInput(
                            attrs=ENTITY_SEARCH_INPUT_ATTRS))


class EADRecordSearchForm(forms.Form):

    q = forms.CharField(required=False, label='Search',
                        widget=forms.TextInput(
                            attrs=RECORD_SEARCH_INPUT_ATTRS))
    start_year = forms.IntegerField(
        required=False, label='Creation start year', widget=forms.NumberInput(
            attrs=RECORD_SEARCH_START_YEAR_INPUT_ATTRS))
    end_year = forms.IntegerField(
        required=False, label='Creation end year', widget=forms.NumberInput(
            attrs=RECORD_SEARCH_END_YEAR_INPUT_ATTRS))


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
                print('{}: {}: {}'.format(type(form), field, field_errors))
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
