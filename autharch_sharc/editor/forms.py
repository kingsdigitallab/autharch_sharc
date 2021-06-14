import calendar
import re
from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from ead.models import (
    EAD,
    Bibliography,
    ControlAccess,
    CustodHist,
    DIdPhysDescStructured,
    DIdPhysDescStructuredDimensions,
    DIdPhysDescStructuredPhysFacet,
    EventDescription,
    LanguageDeclaration,
    MaintenanceEvent,
    Origination,
    OriginationPersName,
    OriginationPersNamePart,
    PhysLoc,
    RelatedMaterial,
    Relation,
    RelationEntry,
    RightsDeclaration,
    ScopeContent,
    Source,
    SourceEntry,
    UnitDate,
    UnitDateStructured,
    UnitDateStructuredDateRange,
    UnitId,
    UnitTitle,
)
from lxml import etree

ENTITY_SEARCH_INPUT_ATTRS = {
    "aria-label": "Search",
    "placeholder": "Search all people and corporate bodies",
    "type": "search",
}

INITIAL_RIGHTS_CITATION = '1.0 Universal (CC0 1.0) Public Domain Dedication'

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

AUDIENCE_HELP = (
    "Indicates whether the record is for public consumption "
    '("external") or not ("internal").'
)


def serialise_xml(element, method="xml"):
    return etree.tostring(
        element, encoding="unicode", method=method, xml_declaration=False
    )


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


class ArchRefInlineForm(forms.Form):

    archref = forms.CharField(
        label="Related entry", required=False, widget=forms.Textarea
    )

    def clean_archref(self):
        item = etree.Element("span")
        item.set("class", "ead-archref")
        item.text = self.cleaned_data["archref"]
        return item


class BibliographyInlineForm(forms.ModelForm):

    # The Bibliography model contains the mixed content in a single
    # textfield, but for this app the contents are constrained to
    # bibref elements, so create a non-model formset for each of them,
    # and manipulate the data into and out of the model field.

    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is not None:
            kwargs.update(initial={"bibliography": self._parse_bibliography(instance)})
        super().__init__(*args, **kwargs)

    def clean_bibliography(self):
        bibrefs = []
        data = (
            self.cleaned_data["bibliography"].replace("\r\n", "\n").replace("\r", "\n")
        )
        for text in data.split("\n\n"):
            bibref = etree.Element("span")
            bibref.set("class", "ead-bibref")
            bibref.text = text
            bibrefs.append(serialise_xml(bibref))
        return "".join(bibrefs)

    def _parse_bibliography(self, instance):
        """Returns the bibrefs in the instance's bibliography field as initial
        data for a non-model formset."""
        bibrefs = []
        root = etree.fromstring("<wrapper>{}</wrapper>".format(instance.bibliography))
        for bibref in root.xpath("//span[@class='ead-bibref']"):
            bibrefs.append(serialise_xml(bibref, method="text"))
        return "\n\n".join(bibrefs)

    class Meta:
        model = Bibliography
        fields = ["bibliography", "id"]
        labels = {
            "bibliography": "Published references",
        }


class ControlAccessInlineForm(ContainerModelForm):
    # controlaccess must be made not required because otherwise an
    # empty field (such as on a new record) fails validation before
    # reaching clean_controlaccess where the content is generated from
    # the non-model inline formsets.
    controlaccess = forms.CharField(required=False, widget=forms.HiddenInput)

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        (
            initial_genreforms,
            initial_geognames,
            initial_persnames,
        ) = self._parse_controlaccess()
        GenreformFormset = forms.formset_factory(
            GenreformInlineForm, extra=1, max_num=1, validate_max=True
        )
        formsets["genreforms"] = GenreformFormset(
            data, initial=initial_genreforms, prefix=self.prefix + "-genreform"
        )
        GeognameFormset = forms.formset_factory(
            GeognameInlineForm, can_delete=True, extra=1, max_num=1, validate_max=True
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
            controlaccess.extend(
                [
                    form.cleaned_data.get(field_name, "")
                    for form in formset.forms
                    if form not in formset.deleted_forms
                ]
            )
        return "".join(controlaccess)

    def has_changed(self):
        # When there is no instance, we want to save so that we
        # capture the data on the non-model inline formsets.
        if self.instance.id is None:
            return True
        return super().has_changed()

    def _parse_controlaccess(self):
        """Returns the genreforms, geognames, and persnames in the instance's
        controlaccess field as initial data for non-model formsets."""
        root = etree.fromstring(
            "<wrapper>{}</wrapper>".format(self.instance.controlaccess)
        )
        genreforms = [
            {"genreform": serialise_xml(genreform, method="text")}
            for genreform in root.xpath("//span[@class='ead-genreform']")
        ]
        geognames = [
            {"geogname": serialise_xml(geogname, method="text")}
            for geogname in root.xpath("//span[@class='ead-geogname']")
        ]
        persnames = [
            {
                "persname": serialise_xml(persname, method="text"),
                "relator": persname.get("data-ead-relator", ""),
            }
            for persname in root.xpath("//span[@class='ead-persname']")
        ]
        return genreforms, geognames, persnames

    class Meta:
        model = ControlAccess
        fields = ["controlaccess", "id"]


class CustodHistInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is not None:
            xml = etree.fromstring("<wrapper>{}</wrapper>".format(instance.custodhist))
            texts = []
            for para in xml.xpath("//p[@class='ead-p']"):
                texts.append(serialise_xml(para, method="text"))
            kwargs.update(initial={"custodhist": "\n\n".join(texts)})
        super().__init__(*args, **kwargs)

    def clean_custodhist(self):
        # Convert consecutive newlines into paragraph breaks.
        paras = []
        data = self.cleaned_data["custodhist"].replace("\r\n", "\n").replace("\r", "\n")
        for para in data.split("\n\n"):
            p = etree.Element("p")
            p.set("class", "ead-p")
            p.text = para
            paras.append(serialise_xml(p))
        return "".join(paras)

    class Meta:
        model = CustodHist
        fields = ["id", "custodhist"]
        labels = {"custodhist": "Provenance"}


class EventDescriptionInlineForm(forms.ModelForm):
    class Meta:
        model = EventDescription
        fields = ["maintenanceevent", "eventdescription", "id"]


class GenreformInlineForm(forms.Form):

    genreform = forms.CharField()

    def clean_genreform(self):
        item = etree.Element("span")
        item.set("class", "ead-genreform")
        item.set("data-ead-source", "AAT")
        part = etree.SubElement(item, "span")
        part.set("class", "ead-part")
        part.text = self.cleaned_data["genreform"]
        return serialise_xml(item)


class GeognameInlineForm(forms.Form):

    geogname = forms.CharField(label="Place of origin", required=False)

    def clean_geogname(self):
        item = etree.Element("span")
        item.set("class", "ead-geogname")
        part = etree.SubElement(item, "span")
        part.set("class", "ead-part")
        part.text = self.cleaned_data["geogname"]
        return serialise_xml(item)


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
            data, instance=self.instance, prefix=self.prefix + "-physfacet"
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
        labels = {
            "physfacet": "Label/inscription/caption",
        }


class LanguageDeclarationInlineForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #for field in ['language_langcode', 'script_el_script']:
        #    self.fields[field].required = True
        #    self.fields[field].widget.is_required = True

    def clean(self):
        # Set the language from the language code.
        cleaned_data = super().clean()
        lang_term = cleaned_data.get("language_langcode")
        if lang_term is not None:
            cleaned_data["language"] = lang_term.label
        return cleaned_data

    class Meta:
        model = LanguageDeclaration
        fields = ["id", "language", "language_langcode", "script_el_script"]
        labels = {
            "language_langcode": "Record language",
            "script_el_script": "Record script",
        }
        widgets = {
            "language": forms.HiddenInput(),
        }


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
            data, instance=self.instance, prefix=self.prefix + "-physfacet"
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
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is not None:
            xml = etree.fromstring("<wrapper>{}</wrapper>".format(instance.physfacet))
            try:
                part = xml.xpath(
                    "span[@class='ead-genreform'][1]/span[@class='ead-part'][1]"
                )[0]
                text = serialise_xml(part, method="text")
            except IndexError:
                text = ""
            kwargs.update(initial={"physfacet": text})
        super().__init__(*args, **kwargs)

    def clean_physfacet(self):
        genreform = etree.Element("span")
        genreform.set("class", "ead-genreform")
        part = etree.SubElement(genreform, "span")
        part.set("class", "ead-part")
        part.text = self.cleaned_data["physfacet"]
        return serialise_xml(genreform)

    class Meta:
        model = DIdPhysDescStructuredPhysFacet
        fields = ["id", "physfacet"]
        labels = {
            "physfacet": "Medium",
        }


class OriginationInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        PersNameFormset = forms.inlineformset_factory(
            Origination,
            OriginationPersName,
            exclude=[],
            form=OriginationPersNameInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["persnames"] = PersNameFormset(
            data, instance=self.instance, prefix=self.prefix + "-persname"
        )
        return formsets

    class Meta:
        model = Origination
        fields = ["id", "label"]


class OriginationPersNameInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        PartFormset = forms.inlineformset_factory(
            OriginationPersName,
            OriginationPersNamePart,
            exclude=[],
            form=OriginationPersNamePartInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["parts"] = PartFormset(
            data, instance=self.instance, prefix=self.prefix + "-part"
        )
        return formsets

    class Meta:
        model = OriginationPersName
        fields = ["id"]


class OriginationPersNamePartInlineForm(forms.ModelForm):

    order = forms.IntegerField(required=False, widget=forms.HiddenInput)

    def clean_order(self):
        order = self.cleaned_data.get("order", 1) or 1
        return order

    class Meta:
        model = OriginationPersNamePart
        fields = ["id", "order", "part"]
        labels = {
            "part": "Creator",
        }
        widgets = {
            "part": forms.TextInput(),
        }


class PersnameNonModelInlineForm(forms.Form):

    persname = forms.CharField(label="Name")
    relator = forms.CharField(label="Association")

    def clean(self):
        cleaned_data = super().clean()
        persname = cleaned_data.get("persname")
        relator = cleaned_data.get("relator")
        if persname is not None and relator:
            persname.set("data-ead-relator", relator)
        cleaned_data["persname"] = serialise_xml(persname)
        return cleaned_data

    def clean_persname(self):
        item = etree.Element("span")
        item.set("class", "ead-persname")
        part = etree.SubElement(item, "span")
        part.set("class", "ead-part")
        part.text = self.cleaned_data["persname"]
        return item


class PhyslocInlineForm(forms.ModelForm):
    class Meta:
        model = PhysLoc
        fields = ["id", "physloc"]
        labels = {
            "physloc": "Physical location",
        }


class RelationEntryInlineForm(forms.ModelForm):
    class Meta:
        model = RelationEntry
        fields = ["id", "localtype", "relationentry"]
        widgets = {
            "localtype": forms.HiddenInput(),
            "relationentry": forms.TextInput(),
        }


class ConnectionTypeInlineForm(RelationEntryInlineForm):
    def clean_localtype(self):
        return "sh_connection_type"

    class Meta(RelationEntryInlineForm.Meta):
        labels = {
            "relationentry": "Individual or works?",
        }


class PrimaryConnectionInlineForm(RelationEntryInlineForm):
    def clean_localtype(self):
        return "work_connection_primary"

    class Meta(RelationEntryInlineForm.Meta):
        labels = {
            "relationentry": "How does it relate to the relevant work?",
        }


class SecondaryConnectionInlineForm(RelationEntryInlineForm):
    def clean_localtype(self):
        return "work_connection_secondary"

    class Meta(RelationEntryInlineForm.Meta):
        labels = {
            "relationentry": "Secondary connection to relevant work?",
        }


class RelatedMaterialInlineForm(ContainerModelForm):
    # relatedmaterial must be made not required because otherwise an
    # empty field (such as on a new record) fails validation before
    # reaching clean_relatedmaterial where the content is generated from
    # the inline formsets.
    relatedmaterial = forms.CharField(required=False, widget=forms.HiddenInput)

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        initial_archrefs = self._parse_relatedmaterial()
        ArchRefFormset = forms.formset_factory(
            ArchRefInlineForm, can_delete=True, extra=0, min_num=1
        )
        formsets["archrefs"] = ArchRefFormset(
            data, initial=initial_archrefs, prefix=self.prefix + "-archref"
        )
        return formsets

    def clean_relatedmaterial(self):
        # Wrap the archrefs in a relatedmaterial, per pcaton's instructions.
        relatedmaterial = etree.Element("span")
        relatedmaterial.set("class", "ead-relatedmaterial")
        formset = self.formsets["archrefs"]
        for form in formset:
            if form not in formset.deleted_forms:
                archref = form.cleaned_data.get("archref")
                if archref is not None:
                    relatedmaterial.append(archref)
        return serialise_xml(relatedmaterial)

    def _parse_relatedmaterial(self):
        """Returns the archref descendants in the instance's relatedmaterial
        field as initial data for non-model formsets."""
        root = etree.fromstring(
            "<wrapper>{}</wrapper>".format(self.instance.relatedmaterial)
        )
        archrefs = [
            {"archref": serialise_xml(archref, method="text")}
            for archref in root.xpath("//span[@class='ead-archref']")
        ]
        return archrefs

    class Meta:
        model = RelatedMaterial
        fields = ["id", "relatedmaterial"]


class RelationInlineForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        ConnectionTypeFormset = forms.inlineformset_factory(
            Relation,
            RelationEntry,
            form=ConnectionTypeInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["connectiontypes"] = ConnectionTypeFormset(
            data,
            instance=self.instance,
            prefix=self.prefix + "-type",
            queryset=RelationEntry.objects.filter(localtype="sh_connection_type"),
        )
        PrimaryConnectionFormset = forms.inlineformset_factory(
            Relation,
            RelationEntry,
            form=PrimaryConnectionInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["primaryconnections"] = PrimaryConnectionFormset(
            data,
            instance=self.instance,
            prefix=self.prefix + "-primary",
            queryset=RelationEntry.objects.filter(localtype="work_connection_primary"),
        )
        SecondaryConnectionFormset = forms.inlineformset_factory(
            Relation,
            RelationEntry,
            form=SecondaryConnectionInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["secondaryconnections"] = SecondaryConnectionFormset(
            data,
            instance=self.instance,
            prefix=self.prefix + "-secondary",
            queryset=RelationEntry.objects.filter(
                localtype="work_connection_secondary"
            ),
        )
        return formsets

    class Meta:
        model = Relation
        fields = ["id"]


class RightsDeclarationInlineForm(forms.ModelForm):

    disabled_fields = ["abbr", "citation"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.disabled_fields:
            self.fields[field].disabled = True

    def clean_citation(self):
        return INITIAL_RIGHTS_CITATION

    def has_changed(self):
        # When there is no instance, we want to save so that we
        # capture the citation.
        if self.instance.id is None:
            return True
        return super().has_changed()

    class Meta:
        model = RightsDeclaration
        fields = ["id", "abbr", "citation", "descriptivenote"]
        labels = {
            "abbr": "Rights declaration abbreviation",
            "citation": "Rights declaration citation",
            "descriptivenote": "Rights declaration",
        }
        widgets = {
            "citation": forms.TextInput(),
        }


class ScopeContentNotesInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is not None:
            xml = etree.fromstring(
                "<wrapper>{}</wrapper>".format(instance.scopecontent)
            )
            texts = []
            for para in xml.xpath("//p[@class='ead-p']"):
                texts.append(serialise_xml(para, method="text"))
            kwargs.update(initial={"scopecontent": "\n\n".join(texts)})
        super().__init__(*args, **kwargs)

    def clean_scopecontent(self):
        # Convert consecutive newlines into paragraph breaks.
        paras = []
        data = (
            self.cleaned_data["scopecontent"].replace("\r\n", "\n").replace("\r", "\n")
        )
        for para in data.split("\n\n"):
            p = etree.Element("p")
            p.set("class", "ead-p")
            p.text = para
            paras.append(serialise_xml(p))
        return "".join(paras)

    class Meta:
        model = ScopeContent
        fields = ["id", "scopecontent"]
        labels = {
            "scopecontent": "Notes",
        }


class ScopeContentPublicationDetailsInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is not None:
            xml = etree.fromstring(
                "<wrapper>{}</wrapper>".format(instance.scopecontent)
            )
            kwargs.update(initial={"scopecontent": serialise_xml(xml, method="text")})
        super().__init__(*args, **kwargs)

    def clean_scopecontent(self):
        item = etree.Element("p")
        item.set("class", "ead-p")
        item.text = self.cleaned_data["scopecontent"]
        return serialise_xml(item)

    class Meta:
        model = ScopeContent
        fields = ["id", "scopecontent"]
        labels = {
            "scopecontent": "Publication details",
        }


class SizeDimensionsInlineForm(forms.ModelForm):
    class Meta:
        model = DIdPhysDescStructuredDimensions
        fields = ["id", "dimensions"]
        labels = {
            "dimensions": "Size",
        }


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
            validate_max=True,
        )
        formsets["dimensions"] = DimensionsFormset(
            data, instance=self.instance, prefix=self.prefix + "-dimensions"
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
        labels = {
            "sourceentry": "Unpublished reference",
        }


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


class UnitDateInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is None:
            kwargs.update(initial={"datechar": self.datechar})
        super().__init__(*args, **kwargs)
        if self.datechar == "creation":
            self.fields["unitdate"].label = "Date of creation notes"
        elif self.datechar == "acquisition":
            self.fields["unitdate"].label = "Date of acquisition notes"

    class Meta:
        model = UnitDate
        fields = ["datechar", "unitdate"]
        widgets = {
            "datechar": forms.HiddenInput(),
        }


class AcquisitionUnitDateInlineForm(UnitDateInlineForm):
    datechar = "acquisition"


class CreationUnitDateInlineForm(UnitDateInlineForm):
    datechar = "creation"


class UDSDateRangeInlineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is not None:
            kwargs.update(
                initial={"display_date": self._assemble_display_date(instance)}
            )
        super().__init__(*args, **kwargs)

    @classmethod
    def _assemble_display_date(cls, instance):
        from_date_iso = instance.fromdate_standarddate
        to_date_iso = instance.todate_standarddate
        if not from_date_iso:
            return ""
        date_format = "%d %B %Y"
        try:
            from_date = date.fromisoformat(from_date_iso).strftime(date_format)
        except ValueError:
            return ""
        if not to_date_iso or to_date_iso == from_date_iso:
            return from_date
        to_date = date.fromisoformat(to_date_iso).strftime(date_format)
        return "{}-{}".format(from_date, to_date)

    def _assemble_range_date(
        self,
        from_day=None,
        from_month=None,
        from_year=None,
        to_day=None,
        to_month=None,
        to_year=None,
    ):
        if from_day is None:
            from_day = 1
            changed_day = True
        else:
            changed_day = False
        if from_month is None:
            from_month = 1
            changed_month = True
        else:
            from_month = self._convert_month(from_month)
            changed_month = False
        if to_year is None:
            to_year = from_year
        else:
            changed = 4 - len(to_year)
            to_year = from_year[:changed] + to_year
        if to_month is None:
            if changed_month:
                to_month = 12
            else:
                to_month = from_month
        else:
            to_month = self._convert_month(to_month)
        if to_day is None:
            if changed_day:
                to_day = self._get_last_day_for_month(to_month, to_year)
            else:
                to_day = from_day
        return (
            date(int(from_year), from_month, int(from_day)),
            date(int(to_year), to_month, int(to_day)),
        )

    @classmethod
    def _convert_month(cls, month):
        months = (
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        )
        return months.index(month) + 1

    @classmethod
    def _get_last_day_for_month(cls, month, year):
        if month in (4, 6, 9, 11):
            day = 30
        elif month == 2:
            if calendar.isleap(year):
                day = 29
            else:
                day = 28
        else:
            day = 31
        return day

    def clean(self):
        # Validate the display date and populate the from and to model
        # fields from its value.
        cleaned_data = super().clean()
        display_date = cleaned_data.get("display_date")
        if display_date is None:
            return cleaned_data
        pattern = r"""
(?:                     # start optional from elements day and month
(?:                     # start optional from element day
(?P<from_day>\d{1,2})   # from day
\s+)?                   # end optional from day element
(?P<from_month>January|February|March|April|May|June|July|August|September
|October|November|December)   # from month
\s+)?                   # end optional from elements day and month
(?P<from_year>\d{4})    # from year
(?:                     # start optional to elements day, month, and year
\s*-\s*                 # hyphen and optional surrounding whitespace
(?:                     # start optional to elements day and month
(?:                     # start optional to elements day
(?P<to_day>\d{1,2})     # to day
\s+)?                   # end optional to day element
(?P<to_month>January|February|March|April|May|June|July|August|September
|October|November|December)     # to month
\s+)?                   # end optional to elements day and month
(?P<to_year>\d{1,4})    # to year
)?                      # end optional to elements day, month, and year
"""
        match = re.fullmatch(pattern, display_date, re.VERBOSE)
        if match is None:
            self.add_error(
                "display_date",
                ValidationError(
                    "Invalid date format: %(value)s",
                    code="invalid",
                    params={"value": display_date},
                ),
            )
        else:
            from_date, to_date = self._assemble_range_date(**match.groupdict())
            cleaned_data["fromdate_standarddate"] = from_date.isoformat()
            cleaned_data["todate_standarddate"] = to_date.isoformat()
        return cleaned_data

    class Meta:
        model = UnitDateStructuredDateRange
        fields = ["id", "fromdate_standarddate", "todate_standarddate"]
        widgets = {
            "fromdate_standarddate": forms.HiddenInput(),
            "todate_standarddate": forms.HiddenInput(),
        }


class AcquisitionUDSDateRangeInlineForm(UDSDateRangeInlineForm):
    display_date = forms.CharField(label="Date of acquisition")


class CreationUDSDateRangeInlineForm(UDSDateRangeInlineForm):
    display_date = forms.CharField(label="Date of creation")


class UnitDateStructuredInlineForm(ContainerModelForm):
    def __init__(self, *args, **kwargs):
        instance = kwargs.get("instance", None)
        if instance is None:
            kwargs.update(initial={"datechar": self.datechar})
        super().__init__(*args, **kwargs)

    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        data = kwargs.get("data")
        DateRangeFormset = forms.inlineformset_factory(
            UnitDateStructured,
            UnitDateStructuredDateRange,
            form=self.date_range_form,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["dateranges"] = DateRangeFormset(
            data, instance=self.instance, prefix=self.prefix + "-daterange"
        )
        return formsets

    class Meta:
        model = UnitDateStructured
        fields = ["id", "datechar"]
        widgets = {
            "datechar": forms.HiddenInput(),
        }


class AcquisitionUnitDateStructuredInlineForm(UnitDateStructuredInlineForm):
    date_range_form = AcquisitionUDSDateRangeInlineForm
    datechar = "acquisition"


class CreationUnitDateStructuredInlineForm(UnitDateStructuredInlineForm):
    date_range_form = CreationUDSDateRangeInlineForm
    datechar = "creation"


class UnitIdInlineForm(forms.ModelForm):
    class Meta:
        model = UnitId
        fields = ["id", "unitid"]


class UnitTitleInlineForm(forms.ModelForm):
    class Meta:
        model = UnitTitle
        fields = ["id", "unittitle"]


class RecordEditForm(ContainerModelForm):
    def _add_formsets(self, *args, **kwargs):
        formsets = {}
        BibliographyFormset = forms.inlineformset_factory(
            EAD,
            Bibliography,
            form=BibliographyInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["bibliographies"] = BibliographyFormset(
            *args, instance=self.instance, prefix="bibliography"
        )
        ControlAccessFormset = forms.inlineformset_factory(
            EAD,
            ControlAccess,
            form=ControlAccessInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["controlaccesses"] = ControlAccessFormset(
            *args, instance=self.instance, prefix="controlaccess"
        )
        CustodHistFormset = forms.inlineformset_factory(
            EAD,
            CustodHist,
            form=CustodHistInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["custodhists"] = CustodHistFormset(
            *args, instance=self.instance, prefix="custodhist"
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
            *args,
            instance=self.instance,
            prefix="label",
            queryset=DIdPhysDescStructured.objects.filter(
                otherphysdescstructuredtype="label_inscription_caption"
            )
        )
        MediumFormset = forms.inlineformset_factory(
            EAD,
            DIdPhysDescStructured,
            form=MediumInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["media"] = MediumFormset(
            *args,
            instance=self.instance,
            prefix="medium",
            queryset=DIdPhysDescStructured.objects.filter(
                physdescstructuredtype=DIdPhysDescStructured.STRUCTURED_TYPE_MATERIAL
            )
        )
        ScopeContentNotesFormset = forms.inlineformset_factory(
            EAD,
            ScopeContent,
            form=ScopeContentNotesInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["notes"] = ScopeContentNotesFormset(
            *args,
            instance=self.instance,
            prefix="scopecontent_notes",
            queryset=ScopeContent.objects.filter(localtype="notes")
        )
        OriginationFormset = forms.inlineformset_factory(
            EAD, Origination, form=OriginationInlineForm, extra=0
        )
        formsets["originations"] = OriginationFormset(
            *args, instance=self.instance, prefix="origination"
        )
        PhysLocFormset = forms.inlineformset_factory(
            EAD,
            PhysLoc,
            form=PhyslocInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["physlocs"] = PhysLocFormset(
            *args, instance=self.instance, prefix="physloc"
        )
        ScopeContentPublicationFormset = forms.inlineformset_factory(
            EAD,
            ScopeContent,
            form=ScopeContentPublicationDetailsInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["publication_details"] = ScopeContentPublicationFormset(
            *args,
            instance=self.instance,
            prefix="scopecontent_publication_details",
            queryset=ScopeContent.objects.filter(localtype="publication_details")
        )
        SizeFormset = forms.inlineformset_factory(
            EAD,
            DIdPhysDescStructured,
            form=SizeInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["sizes"] = SizeFormset(
            *args,
            instance=self.instance,
            prefix="size",
            queryset=DIdPhysDescStructured.objects.filter(
                physdescstructuredtype=DIdPhysDescStructured.STRUCTURED_TYPE_SPACE
            )
        )
        SourceFormset = forms.inlineformset_factory(
            EAD, Source, form=SourceInlineForm, extra=0
        )
        formsets["sources"] = SourceFormset(
            *args, instance=self.instance, prefix="source"
        )
        CreationDateFormset = forms.inlineformset_factory(
            EAD,
            UnitDateStructured,
            form=CreationUnitDateStructuredInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["creation_dates"] = CreationDateFormset(
            *args,
            instance=self.instance,
            prefix="creation_date",
            queryset=UnitDateStructured.objects.filter(datechar="creation")
        )
        CreationDateNoteFormset = forms.inlineformset_factory(
            EAD,
            UnitDate,
            form=CreationUnitDateInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["creation_date_notes"] = CreationDateNoteFormset(
            *args,
            instance=self.instance,
            prefix="creation_date_note",
            queryset=UnitDate.objects.filter(datechar="creation")
        )
        AcquisitionDateFormset = forms.inlineformset_factory(
            EAD,
            UnitDateStructured,
            form=AcquisitionUnitDateStructuredInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["acquisition_dates"] = AcquisitionDateFormset(
            *args,
            instance=self.instance,
            prefix="acquisition_date",
            queryset=UnitDateStructured.objects.filter(datechar="acquisition")
        )
        AcquisitionDateNoteFormset = forms.inlineformset_factory(
            EAD,
            UnitDate,
            form=AcquisitionUnitDateInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["acquisition_date_notes"] = AcquisitionDateNoteFormset(
            *args,
            instance=self.instance,
            prefix="acquisition_date_note",
            queryset=UnitDate.objects.filter(datechar="acquisition")
        )
        UnitIdFormset = forms.inlineformset_factory(
            EAD,
            UnitId,
            form=UnitIdInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["unitids"] = UnitIdFormset(
            *args, instance=self.instance, prefix="unitid"
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
            *args, instance=self.instance, prefix="unittitle"
        )
        RelationFormset = forms.inlineformset_factory(
            EAD,
            Relation,
            form=RelationInlineForm,
            extra=0,
            min_num=1,
            validate_min=True,
        )
        formsets["relations"] = RelationFormset(
            *args,
            instance=self.instance,
            prefix="relation",
            queryset=Relation.objects.filter(otherrelationtype="sh_connection")
        )
        RelatedMaterialFormset = forms.inlineformset_factory(
            EAD,
            RelatedMaterial,
            form=RelatedMaterialInlineForm,
            extra=1,
            max_num=1,
            validate_max=True,
        )
        formsets["relatedmaterials"] = RelatedMaterialFormset(
            *args, instance=self.instance, prefix="relatedmaterial"
        )
        LanguageDeclarationFormset = forms.inlineformset_factory(
            EAD,
            LanguageDeclaration,
            form=LanguageDeclarationInlineForm,
            extra=1,
            max_num=1,
            min_num=0,
            validate_max=True,
            validate_min=True,
        )
        formsets["languagedeclarations"] = LanguageDeclarationFormset(
            *args, instance=self.instance, prefix="languagedeclaration"
        )
        RightsDeclarationFormset = forms.inlineformset_factory(
            EAD,
            RightsDeclaration,
            form=RightsDeclarationInlineForm,
            extra=1,
            max_num=1,
            min_num=1,
            validate_max=True,
            validate_min=True,
        )
        formsets["rightsdeclarations"] = RightsDeclarationFormset(
            *args, instance=self.instance, prefix="rightsdeclaration",
            initial=[{'citation': INITIAL_RIGHTS_CITATION}],
        )
        return formsets

    class Meta:
        model = EAD
        fields = ["audience", "recordid"]
        help_texts = {
            "audience": AUDIENCE_HELP,
        }


class EADEntitySearchForm(forms.Form):

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs=ENTITY_SEARCH_INPUT_ATTRS),
    )


class EADRecordSearchForm(forms.Form):

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs=RECORD_SEARCH_INPUT_ATTRS),
    )
    creation_start_year = forms.IntegerField(
        required=False,
        label="Creation start year",
        widget=forms.NumberInput(attrs=RECORD_SEARCH_START_YEAR_INPUT_ATTRS),
    )
    creation_end_year = forms.IntegerField(
        required=False,
        label="Creation end year",
        widget=forms.NumberInput(attrs=RECORD_SEARCH_END_YEAR_INPUT_ATTRS),
    )
    acquisition_start_year = forms.IntegerField(
        required=False,
        label="Acquisition start year",
        widget=forms.NumberInput(attrs=RECORD_SEARCH_START_YEAR_INPUT_ATTRS),
    )
    acquisition_end_year = forms.IntegerField(
        required=False,
        label="Acquisition end year",
        widget=forms.NumberInput(attrs=RECORD_SEARCH_END_YEAR_INPUT_ATTRS),
    )

    def __init__(
        self,
        *args,
        creation_min_year=0,
        creation_max_year=2040,
        acquisition_min_year=0,
        acquisition_max_year=2040,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        acquisition_start_widget = self.fields["acquisition_start_year"].widget
        acquisition_start_widget.attrs["min"] = acquisition_min_year
        acquisition_start_widget.attrs["max"] = acquisition_max_year
        acquisition_start_widget.attrs["placeholder"] = acquisition_min_year
        acquisition_end_widget = self.fields["acquisition_end_year"].widget
        acquisition_end_widget.attrs["min"] = acquisition_min_year
        acquisition_end_widget.attrs["max"] = acquisition_max_year
        acquisition_end_widget.attrs["placeholder"] = acquisition_max_year
        creation_start_widget = self.fields["creation_start_year"].widget
        creation_start_widget.attrs["min"] = creation_min_year
        creation_start_widget.attrs["max"] = creation_max_year
        creation_start_widget.attrs["placeholder"] = creation_min_year
        creation_end_widget = self.fields["creation_end_year"].widget
        creation_end_widget.attrs["min"] = creation_min_year
        creation_end_widget.attrs["max"] = creation_max_year
        creation_end_widget.attrs["placeholder"] = creation_max_year
        self._acquisition_min_year = acquisition_min_year
        self._acquisition_max_year = acquisition_max_year
        self._creation_min_year = creation_min_year
        self._creation_max_year = creation_max_year


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
