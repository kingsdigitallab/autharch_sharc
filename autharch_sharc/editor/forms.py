from django import forms
from ead.constants import NS_MAP
from ead.models import (
    EAD,
    Bibliography,
    ControlAccess,
    CorpName,
    CorpNamePart,
    CustodHist,
    DIdPhysDescStructured,
    DIdPhysDescStructuredDimensions,
    DIdPhysDescStructuredPhysFacet,
    EventDescription,
    MaintenanceEvent,
    Origination,
    PersName,
    PersNamePart,
    PhysLoc,
    ScopeContent,
    Source,
    SourceEntry,
    UnitDateStructured,
    UnitDateStructuredDateRange,
    UnitTitle,
)
from lxml import etree

RECORD_SEARCH_INPUT_ATTRS = {
    "aria-label": "Search",
    "placeholder": "Search all archival records",
    "type": "search",
}

RECORD_SEARCH_START_YEAR_INPUT_ATTRS = {
    "aria-label": "Start year",
}

RECORD_SEARCH_END_YEAR_INPUT_ATTRS = {
    "aria-label": "End year",
}


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
        return bool(self.changed_data) or any(
            formset.has_changed() for formset in self.formsets.values()
        )

    def is_valid(self):
        return super().is_valid() and all(
            formset.is_valid() for formset in self.formsets.values()
        )

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
        data = kwargs.get("data")
        initial_bibrefs = self._parse_bibliography()
        BibRefFormset = forms.formset_factory(
            BibRefForm, can_delete=True, extra=0, min_num=1, validate_min=True
        )
        formsets["bibrefs"] = BibRefFormset(
            data, initial=initial_bibrefs, prefix=self.prefix + "-bibref"
        )
        return formsets

    def clean_bibliography(self):
        formset = self.formsets["bibrefs"]
        bibrefs = [
            form.cleaned_data["bibref"]
            for form in formset.forms
            if form not in formset.deleted_forms
        ]
        bibliography = "".join(bibrefs)
        return bibliography

    def _parse_bibliography(self):
        """Returns the bibrefs in the instance's bibliography field as initial
        data for a non-model formset."""
        bibrefs = []
        root = etree.fromstring(
            "<wrapper>{}</wrapper>".format(self.instance.bibliography)
        )
        for bibref in root.xpath("//e:bibref", namespaces=NS_MAP):
            bibrefs.append(
                {
                    "bibref": etree.tostring(
                        bibref, encoding="unicode", xml_declaration=False
                    )
                }
            )
        return bibrefs

    class Meta:
        model = Bibliography
        fields = ["archdesc", "bibliography", "id"]


class BibRefForm(forms.Form):
    bibref = forms.CharField(widget=forms.Textarea)


class ControlAccessInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        (
            initial_genreforms,
            initial_geognames,
            initial_persnames,
        ) = self._parse_controlaccess()
        GenreformFormset = forms.formset_factory(
            GenreformInlineForm, can_delete=True, extra=0
        )
        formsets["genreforms"] = GenreformFormset(
            data, initial=initial_genreforms, prefix=self.prefix + "-genreform"
        )
        GeognameFormset = forms.formset_factory(
            GeognameInlineForm, can_delete=True, extra=0
        )
        formsets["geognames"] = GeognameFormset(
            data, initial=initial_geognames, prefix=self.prefix + "-geogname"
        )
        PersnameFormset = forms.formset_factory(
            PersnameNonModelInlineForm, can_delete=True, extra=0
        )
        formsets["persnames"] = PersnameFormset(
            data, initial=initial_persnames, prefix=self.prefix + "-persname"
        )
        return formsets

    def clean_controlaccess(self):
        controlaccess = []
        subs = [
            ("genreforms", "genreform"),
            ("geognames", "geogname"),
            ("persnames", "persname"),
        ]
        for formset_name, field_name in subs:
            formset = self.formsets[formset_name]
            controlaccess.append(
                [
                    form.cleaned_data[field_name]
                    for form in formset.forms
                    if form not in formset.deleted_forms
                ]
            )
        return "".join(controlaccess)

    def _parse_controlaccess(self):
        """Returns the genreforms, geognames, and persnames in the instance's
        controlaccess field as initial data for non-model formsets."""
        root = etree.fromstring(
            "<wrapper>{}</wrapper>".format(self.instance.controlaccess)
        )
        genreforms = [
            {
                "genreform": etree.tostring(
                    genreform, encoding="unicode", xml_declaration=False
                )
            }
            for genreform in root.xpath("//e:genreform", namespaces=NS_MAP)
        ]
        geognames = [
            {
                "geogname": etree.tostring(
                    geogname, encoding="unicode", xml_declaration=False
                )
            }
            for geogname in root.xpath("//e:geogname", namespaces=NS_MAP)
        ]
        persnames = [
            {
                "persname": etree.tostring(
                    persname, encoding="unicode", xml_declaration=False
                )
            }
            for persname in root.xpath("//e:persname", namespaces=NS_MAP)
        ]
        return genreforms, geognames, persnames

    class Meta:
        model = ControlAccess
        fields = ["controlaccess", "id"]


class CorpNameInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        CorpNamePartFormset = forms.inlineformset_factory(
            CorpName,
            CorpNamePart,
            form=CorpNamePartInlineForm,
            extra=0,
            max_num=1,
            validate_max=True,
        )
        formsets["parts"] = CorpNamePartFormset(
            data, instance=self.instance, prefix=self.prefix + "-part"
        )
        return formsets

    class Meta:
        model = CorpName
        fields = ["id"]


class CorpNamePartInlineForm(forms.ModelForm):
    class Meta:
        model = CorpNamePart
        fields = ["id", "part"]


class CustodHistInlineForm(forms.ModelForm):
    class Meta:
        model = CustodHist
        fields = ["id", "custodhist"]


class EventDescriptionInlineForm(forms.ModelForm):
    class Meta:
        model = EventDescription
        fields = ["maintenanceevent", "eventdescription", "id"]


class GenreformInlineForm(forms.Form):

    genreform = forms.CharField()


class GeognameInlineForm(forms.Form):

    geogname = forms.CharField()


class LabelInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        PhysFacetFormset = forms.inlineformset_factory(
            DIdPhysDescStructured,
            DIdPhysDescStructuredPhysFacet,
            form=LabelPhysFacetInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["physfacets"] = PhysFacetFormset(
            data, instance=self.instance, prefix="physfacet"
        )
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.physdescstructuredtype = (
                DIdPhysDescStructured.STRUCTURED_TYPE_OTHER
            )
            self.instance.otherphysdescstructuredtype = "label_inscription_caption"
            self.instance.quantity = 1
            self.instance.unittype = "item"
            self.instance.coverage = DIdPhysDescStructured.COVERAGE_PART
        super().save(commit)

    class Meta:
        model = DIdPhysDescStructured
        fields = ["id"]


class LabelPhysFacetInlineForm(forms.ModelForm):
    class Meta:
        model = DIdPhysDescStructuredPhysFacet
        fields = ["id", "physfacet"]


class MaintenanceEventInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        EventDescriptionFormset = forms.inlineformset_factory(
            MaintenanceEvent,
            EventDescription,
            form=EventDescriptionInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["eventdescriptions"] = EventDescriptionFormset(
            data, instance=self.instance, prefix=self.prefix + "-eventdescription"
        )
        return formsets

    class Meta:
        model = MaintenanceEvent
        fields = [
            "id",
            "maintenancehistory",
            "agent",
            "agenttype_value",
            "eventtype_value",
        ]


class MediumInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        PhysFacetFormset = forms.inlineformset_factory(
            DIdPhysDescStructured,
            DIdPhysDescStructuredPhysFacet,
            form=MediumPhysFacetInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["physfacets"] = PhysFacetFormset(
            data, instance=self.instance, prefix="physfacet"
        )
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.physdescstructuredtype = (
                DIdPhysDescStructured.STRUCTURED_TYPE_MATERIAL
            )
            self.instance.quantity = 1
            self.instance.unittype = "item"
            self.instance.coverage = DIdPhysDescStructured.COVERAGE_WHOLE
        super().save(commit)

    class Meta:
        model = DIdPhysDescStructured
        fields = ["id"]


class MediumPhysFacetInlineForm(forms.ModelForm):
    class Meta:
        model = DIdPhysDescStructuredPhysFacet
        fields = ["id", "physfacet"]


class OriginationInlineForm(forms.ModelForm):
    class Meta:
        model = Origination
        fields = ["id", "corpnames", "label", "persnames"]


class PersNameInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        PartFormset = forms.inlineformset_factory(
            PersName,
            PersNamePart,
            form=PersNamePartInlineForm,
            extra=0,
            max_num=1,
            validate_max=True,
        )
        formsets["parts"] = PartFormset(
            data, instance=self.instance, prefix=self.prefix + "-part"
        )
        return formsets

    class Meta:
        model = PersName
        fields = ["id"]


class PersNamePartInlineForm(forms.ModelForm):
    class Meta:
        model = PersNamePart
        fields = ["id", "part"]


class PersnameNonModelInlineForm(forms.Form):

    persname = forms.CharField()


class PhyslocInlineForm(forms.ModelForm):
    class Meta:
        model = PhysLoc
        fields = ["id", "physloc"]


class ScopeContentInlineForm(forms.ModelForm):
    class Meta:
        model = ScopeContent
        fields = ["id", "scopecontent"]


class SizeDimensionsInlineForm(forms.ModelForm):
    class Meta:
        model = DIdPhysDescStructuredDimensions
        fields = ["id", "dimensions"]


class SizeInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        DimensionsFormset = forms.inlineformset_factory(
            DIdPhysDescStructured,
            DIdPhysDescStructuredDimensions,
            form=SizeDimensionsInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["sizes"] = DimensionsFormset(
            data, instance=self.instance, prefix="physfacet"
        )
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.physdescstructuredtype = (
                DIdPhysDescStructured.STRUCTURED_TYPE_SPACE
            )
            self.instance.quantity = 1
            self.instance.unittype = "item"
            self.instance.coverage = DIdPhysDescStructured.COVERAGE_WHOLE
        super().save(commit)

    class Meta:
        model = DIdPhysDescStructured
        fields = ["id"]


class SourceEntryInlineForm(forms.ModelForm):
    class Meta:
        model = SourceEntry
        fields = ["id", "sourceentry"]


class SourceInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        SourceEntryFormset = forms.inlineformset_factory(
            Source, SourceEntry, form=SourceEntryInlineForm, extra=0
        )
        formsets["sourceentries"] = SourceEntryFormset(
            data, instance=self.instance, prefix=self.prefix + "-sourceentry"
        )
        return formsets

    class Meta:
        model = Source
        fields = ["id"]


class UnitDateStructuredDateRangeInlineForm(forms.ModelForm):
    class Meta:
        model = UnitDateStructuredDateRange
        fields = ["id", "fromdate_standarddate", "todate_standarddate"]


class UnitDateStructuredInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        DateRangeFormset = forms.inlineformset_factory(
            UnitDateStructured,
            UnitDateStructuredDateRange,
            form=UnitDateStructuredDateRangeInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["dateranges"] = DateRangeFormset(
            data, instance=self.instance, prefix=self.prefix + "-daterange"
        )
        return formsets

    def save(self, commit=True):
        if not self.errors:
            self.instance.datechar = "creation"
        super().save(commit)

    class Meta:
        model = UnitDateStructured
        fields = ["id"]


class UnitTitleInlineForm(forms.ModelForm):
    class Meta:
        model = UnitTitle
        fields = ["id", "unittitle"]


class EADContentForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        BibliographyFormset = forms.inlineformset_factory(
            EAD,
            Bibliography,
            form=BibliographyInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["bibliographies"] = BibliographyFormset(
            data, instance=self.instance, prefix="bibliography"
        )
        ControlAccessFormset = forms.inlineformset_factory(
            EAD,
            ControlAccess,
            form=ControlAccessInlineForm,
            extra=0,
            max_num=1,
            validate_max=True,
        )
        formsets["controlaccesses"] = ControlAccessFormset(
            data, instance=self.instance, prefix="controlaccess"
        )
        CustodHistFormset = forms.inlineformset_factory(
            EAD, CustodHist, form=CustodHistInlineForm, extra=0
        )
        formsets["custodhists"] = CustodHistFormset(
            data, instance=self.instance, prefix="custodhist"
        )
        LabelFormset = forms.inlineformset_factory(
            EAD,
            DIdPhysDescStructured,
            form=LabelInlineForm,
            extra=0,
            max_num=1,
            validate_max=True,
        )
        formsets["labels"] = LabelFormset(
            data,
            instance=self.instance,
            prefix="label",
            queryset=DIdPhysDescStructured.objects.filter(
                otherphysdescstructuredtype="label_inscription_caption"
            ),
        )
        MediumFormset = forms.inlineformset_factory(
            EAD, DIdPhysDescStructured, form=MediumInlineForm, extra=0
        )
        formsets["media"] = MediumFormset(
            data,
            instance=self.instance,
            prefix="medium",
            queryset=DIdPhysDescStructured.objects.filter(
                physdescstructuredtype=DIdPhysDescStructured.STRUCTURED_TYPE_MATERIAL
            ),
        )
        ScopeContentFormset = forms.inlineformset_factory(
            EAD,
            ScopeContent,
            form=ScopeContentInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["notes"] = ScopeContentFormset(
            data,
            instance=self.instance,
            prefix="scopecontent_notes",
            queryset=ScopeContent.objects.filter(localtype="notes"),
        )
        OriginationFormset = forms.inlineformset_factory(
            EAD, Origination, form=OriginationInlineForm, extra=0
        )
        formsets["originations"] = OriginationFormset(
            data, instance=self.instance, prefix="origination"
        )
        PhysLocFormset = forms.inlineformset_factory(
            EAD, PhysLoc, form=PhyslocInlineForm, extra=0
        )
        formsets["physlocs"] = PhysLocFormset(
            data, instance=self.instance, prefix="physloc"
        )
        formsets["publication_details"] = ScopeContentFormset(
            data,
            instance=self.instance,
            prefix="scopecontent_publication_details",
            queryset=ScopeContent.objects.filter(localtype="publication_details"),
        )
        SizeFormset = forms.inlineformset_factory(
            EAD, DIdPhysDescStructured, form=SizeInlineForm, extra=0
        )
        formsets["sizes"] = SizeFormset(
            data,
            instance=self.instance,
            prefix="size",
            queryset=DIdPhysDescStructured.objects.filter(
                physdescstructuredtype=DIdPhysDescStructured.STRUCTURED_TYPE_SPACE
            ),
        )
        SourceFormset = forms.inlineformset_factory(
            EAD, Source, form=SourceInlineForm, extra=0
        )
        formsets["sources"] = SourceFormset(
            data, instance=self.instance, prefix="source"
        )
        UnitDateStructuredFormset = forms.inlineformset_factory(
            EAD,
            UnitDateStructured,
            form=UnitDateStructuredInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["unitdatestructureds"] = UnitDateStructuredFormset(
            data,
            instance=self.instance,
            prefix="unitdatestructured",
            queryset=UnitDateStructured.objects.filter(datechar="creation"),
        )
        UnitTitleFormset = forms.inlineformset_factory(
            EAD,
            UnitTitle,
            form=UnitTitleInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["unittitles"] = UnitTitleFormset(
            data, instance=self.instance, prefix="unittitle"
        )
        return formsets

    class Meta:
        model = EAD
        fields = ["recordid"]


class EADMaintenanceForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        MaintenanceEventFormset = forms.inlineformset_factory(
            EAD,
            MaintenanceEvent,
            form=MaintenanceEventInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["maintenanceevents"] = MaintenanceEventFormset(
            data, instance=self.instance, prefix="maintenanceevent"
        )
        return formsets

    class Meta:
        model = EAD
        fields = ["maintenancestatus_value", "publicationstatus_value"]


class EADSearchForm(forms.Form):

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs=RECORD_SEARCH_INPUT_ATTRS),
    )
    start_year = forms.IntegerField(
        required=False,
        label="Creation start year",
        widget=forms.NumberInput(attrs=RECORD_SEARCH_START_YEAR_INPUT_ATTRS),
    )
    end_year = forms.IntegerField(
        required=False,
        label="Creation end year",
        widget=forms.NumberInput(attrs=RECORD_SEARCH_END_YEAR_INPUT_ATTRS),
    )


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
            if field == "__all__":
                errors["non_field"].extend(field_errors)
            else:
                errors["field"] = True
        if hasattr(form, "formsets"):
            for formset in form.formsets.values():
                for form in formset.forms:
                    errors = add_form_errors(errors, form)
        return errors

    errors = {"field": False, "non_field": []}
    errors = add_form_errors(errors, form)
    if not (errors["field"] or errors["non_field"]):
        errors = {}
    return errors
