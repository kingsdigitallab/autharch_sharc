import re

import requests
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from ead.models import (
    EAD,
    DIdPhysDescStructuredDimensions,
    RelationEntry,
    SourceEntry,
    UnitDateStructuredDateRange,
)
from elasticsearch_dsl import analyzer, normalizer
from lxml import etree

from autharch_sharc.editor.models import SharcIIIF

html_strip_analyzer = analyzer(
    "html_strip", tokenizer="standard", char_filter=["html_strip"]
)

lowercase_sort_normalizer = normalizer(
    "lowercase_sort", filter=["lowercase", "asciifolding"]
)

"""
Search fields for EAD document searching
Included here so we can use it in api view and in building search content
"""
eaddocument_search_fields = (
    "unittitle",
    "reference",
    "category",
    "connection_primary",
    "related_sources.works",
    "related_sources.texts",
    "related_sources.performances",
    "related_sources.sources",
    "related_sources.individuals",
    "acquirer",
    "label",
)


@registry.register_document
class EADDocument(Document):
    """ Document model for EAD objects uploaded via xml"""

    """ Used for iiif images while we wait for them"""
    default_iiif_manifest_url = "PLACEHOLDER"
    default_full_image_url = "PLACEHOLDER"
    default_iiif_image_url = "PLACEHOLDER"
    default_thumbnail_url = "PLACEHOLDER"
    default_doc_type = "object"

    class Index:
        name = "editor"

    class Django:
        model = EAD
        fields = [
            "maintenancestatus_value",
            "recordid",
        ]

    creators = fields.ObjectField(
        properties={
            "key": fields.KeywordField(),
            "name": fields.TextField(),
        }
    )
    pk = fields.IntegerField(attr="id")
    reference = fields.KeywordField()
    archdesc_level = fields.KeywordField(attr="archdesc_level")
    provenance = fields.ObjectField(
        properties={
            "raw": fields.TextField(),
            "html": fields.TextField(analyzer=html_strip_analyzer),
        }
    )
    notes = fields.ObjectField(
        properties={
            "raw": fields.TextField(),
            "html": fields.TextField(analyzer=html_strip_analyzer),
        }
    )
    references_published = fields.ObjectField(
        properties={
            "raw": fields.TextField(),
            "html": fields.TextField(analyzer=html_strip_analyzer),
        }
    )
    references_unpublished = fields.ObjectField(
        properties={
            "raw": fields.TextField(),
            "html": fields.TextField(analyzer=html_strip_analyzer),
        }
    )
    category = fields.KeywordField(
        fields={
            "lowercase": fields.KeywordField(normalizer=lowercase_sort_normalizer),
            "suggest": fields.CompletionField(),
        }
    )
    # stories = fields.ObjectField(
    #     properties={
    #         "story": fields.KeywordField(),
    #         "connection_type": fields.KeywordField(),
    #     }
    # )
    # themes = fields.TextField(
    #     fields={
    #         "raw": fields.KeywordField(),
    #         "lowercase": fields.KeywordField(normalizer=lowercase_sort_normalizer),
    #     }
    # )
    related_people = fields.ObjectField(
        properties={
            "acquirers": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
            "donors": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
            "publishers": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
        }
    )

    place_of_origin = fields.KeywordField()
    related_sources = fields.ObjectField(
        properties={
            "individuals": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
            "works": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
            "texts": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
            "sources": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
            "performances": fields.KeywordField(
                fields={
                    "suggest": fields.CompletionField(),
                }
            ),
        }
    )
    connection_primary = fields.KeywordField()
    connection_secondary = fields.KeywordField()
    """ todo Will need to be rafactored once we know more"""
    media = fields.ObjectField(
        properties={
            "label": fields.TextField(),
            "iiif_manifest_url": fields.TextField(),
            "iiif_image_url": fields.TextField(),
            "full_image_url": fields.TextField(),
            "thumbnail_url": fields.TextField(),
            "image_width": fields.IntegerField(),
            "image_height": fields.IntegerField(),
            "thumbnail_width": fields.IntegerField(),
            "thumbnail_height": fields.IntegerField(),
        }
    )

    related_material = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    connection_type = fields.KeywordField()
    date_of_acquisition = fields.IntegerField()
    date_of_creation = fields.IntegerField()
    publicationstatus_value = fields.KeywordField()
    unittitle = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
            "sort": fields.KeywordField(normalizer=lowercase_sort_normalizer),
            "suggest": fields.CompletionField(),
        }
    )
    size = fields.KeywordField()
    medium = fields.KeywordField()
    label = fields.KeywordField()
    doc_type = fields.KeywordField()
    is_visible = fields.BooleanField()

    search_content = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
            "sort": fields.KeywordField(normalizer=lowercase_sort_normalizer),
        }
    )

    def prepare_is_visible(self, instance):
        if instance.audience == "internal":
            return False
        return True

    # def prepare_themes(self, instance):
    #
    #     if (
    #         ThemeObjectCollection.objects.filter(
    #             theme_objects__ead_snippet__ead=instance
    #         ).count()
    #         > 0
    #     ):
    #         return [
    #             theme.title
    #             for theme in ThemeObjectCollection.objects.filter(
    #                 theme_objects__ead_snippet__ead=instance
    #             )
    #         ]
    #     return []
    #
    # def prepare_stories(self, instance):
    #     """ EAD Group Objects"""
    #     stories = []
    #     for story_object in StoryObject.objects.filter(ead_snippet__ead=instance):
    #         stories.append(
    #             {
    #                 "story": story_object.story.title,
    #                 "connection_type": story_object.connection_type.type,
    #             }
    #         )
    #     return stories

    def prepare_doc_type(self, instance):
        return self.default_doc_type

    def prepare_search_content(self, instance):
        """Deliberately empty so we can instantiate this at
        the end in prepare"""
        return ""

    def get_search_content(self, data):
        """Run after all other fields prepared to ensure
        fields are populated"""
        content = ""
        for field in eaddocument_search_fields:
            if field in data:
                content = content + " " + str(data[field])
        return content

    def prepare(self, instance):
        data = super().prepare(instance)
        data["search_content"] = self.get_search_content(data)
        return data

    def prepare_media(self, instance):
        """
        This is mostly a placeholder for now
        will add live data when we get it
        """

        media = []

        iiif_manifest_url = self.default_iiif_manifest_url
        full_image_url = self.default_full_image_url
        iiif_image_url = self.default_iiif_image_url
        thumbnail_url = self.default_thumbnail_url
        image_width = 4015
        image_height = 2980
        thumbnail_width = 175
        thumbnail_height = 130
        label = "1"
        # Try to fetch the iiif manifest
        RCIN = self.prepare_reference(instance)
        if SharcIIIF.objects.filter(rcin=RCIN).count() > 0:
            for iiif_record in SharcIIIF.objects.filter(rcin=RCIN):
                manifest_url = iiif_record.iiif_uri
                try:
                    r = requests.get(manifest_url)
                    # todo change this if excel format changes
                    label = iiif_record.images_available
                    if r.status_code == 200 and len(r.text) > 0:
                        # It's there, parse it
                        response = r.json()
                        # print(manifest_url)

                        try:
                            if (
                                "sequences" in response
                                and len(response["sequences"]) > 0
                            ):
                                iiif_manifest_url = manifest_url
                                for canvas in response["sequences"][0]["canvases"]:
                                    image = canvas["images"][0]
                                    # Full size image
                                    full_image_url = image["resource"]["@id"]
                                    iiif_image_url = image["resource"]["service"]["@id"]
                                    iiif_image_url = iiif_image_url.replace(
                                        "https://rct.resourcespace.com/", "/rct/"
                                    )
                                    if "width" in image["resource"]:
                                        image_width = image["resource"]["width"]
                                    if "height" in image["resource"]:
                                        image_height = image["resource"]["height"]
                                    # Thumbnail
                                    if "thumbnail" in canvas:
                                        thumbnail = canvas["thumbnail"]
                                        thumbnail_url = thumbnail["@id"]
                                        if "width" in thumbnail:
                                            thumbnail_width = thumbnail["width"]
                                        if "height" in thumbnail:
                                            thumbnail_height = thumbnail["height"]
                        except IndexError:
                            pass
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.MissingSchema,
                ):
                    print("BaD url! {}\n".format(manifest_url))
                media.append(
                    {
                        "label": label,
                        "iiif_manifest_url": iiif_manifest_url,
                        "iiif_image_url": iiif_image_url,
                        "full_image_url": full_image_url,
                        "thumbnail_url": thumbnail_url,
                        "image_width": image_width,
                        "image_height": image_height,
                        "thumbnail_width": thumbnail_width,
                        "thumbnail_height": thumbnail_height,
                    }
                )
        # if 'metadata' in response:
        #     for data in response['metadata']:
        #         if data['label'] == 'Title':
        #             title = data['value']

        if len(media) > 0:
            return media
        else:
            # Return placeholders for now
            return [
                {
                    "label": label,
                    "iiif_manifest_url": iiif_manifest_url,
                    "iiif_image_url": iiif_image_url,
                    "full_image_url": full_image_url,
                    "thumbnail_url": thumbnail_url,
                    "image_width": image_width,
                    "image_height": image_height,
                    "thumbnail_width": thumbnail_width,
                    "thumbnail_height": thumbnail_height,
                }
            ]

    def prepare_place_of_origin(self, instance):
        if len(instance.originalsloc_set.all()) > 0:
            return [
                originalsloc.originalsloc
                for originalsloc in instance.originalsloc_set.all()
            ][0]
        return []

    def prepare_reference(self, instance):
        if len(instance.unitid_set.all()) > 0:
            return [unitid.unitid for unitid in instance.unitid_set.all()][0]
        return 0

    #
    def prepare_size(self, instance):
        size = ""
        for physdescstructured in instance.physdescstructured_set.all():
            if physdescstructured.physdescstructuredtype == "spaceoccupied":
                size = "{} {}".format(
                    physdescstructured.quantity, physdescstructured.unittype
                )
                for dim in DIdPhysDescStructuredDimensions.objects.filter(
                    physdescstructured=physdescstructured
                ):
                    if dim.dimensions and len(dim.dimensions) > 0:
                        size = size + "; {}".format(dim.dimensions)

        return size

    def prepare_medium(self, instance):
        medium = ""
        for physdescstructured in instance.physdescstructured_set.all():
            if physdescstructured.physdescstructuredtype == "materialtype":
                for phys in physdescstructured.physfacet_set.all():
                    root = etree.fromstring(
                        "<wrapper>{}</wrapper>".format(phys.physfacet)
                    )
                    for media in root.xpath(
                        "span[@class='ead-genreform']/span[" "@class='ead-part']/text()"
                    ):
                        medium = medium + media
        return medium

    def prepare_label(self, instance):
        label = ""
        for physdescstructured in instance.physdescstructured_set.all():
            if (
                physdescstructured.otherphysdescstructuredtype
                == "label_inscription_caption"
            ):
                for phys in physdescstructured.physfacet_set.all():
                    label = label + "{}".format(phys.physfacet)
        return label

    def _get_year_from_date(self, date):
        try:
            year_end_index = date.index("-")
            year = int(date[:year_end_index])
        except ValueError:
            try:
                year = int(date)
            except ValueError:
                year = None
        return year

    def _get_year_range(self, instance, datechar):
        try:
            date_range = UnitDateStructuredDateRange.objects.get(
                parent__did=instance, parent__datechar=datechar
            )
        except UnitDateStructuredDateRange.DoesNotExist:
            return []
        start_year = self._get_year_from_date(date_range.fromdate_standarddate)
        end_year = self._get_year_from_date(date_range.todate_standarddate)
        if start_year is None:
            years = []
        elif end_year is None:
            years = [start_year]
        else:
            years = list(range(start_year, end_year + 1))
        return years

    def prepare_category(self, instance):
        # It is required for this project that there be one and only
        # one category, though EAD3 allows many.
        categories = []
        for controlaccess in instance.controlaccess_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(controlaccess.controlaccess)
            )
            categories.extend(
                [
                    str(category).strip()
                    for category in root.xpath(
                        "span[@class='ead-genreform']/span[" "@class='ead-part']/text()"
                    )
                ]
            )
        if len(categories) > 0:
            return categories[0]
        elif len(root.xpath("span[@class='ead-genreform']/text()")) > 0:
            # try a different pattern
            return root.xpath("span[@class='ead-genreform']/text()")
        return ""

    def _prepare_connection(self, instance, localtype):
        connections = []
        for relationentry in RelationEntry.objects.filter(
            relation__relations=instance, localtype=localtype
        ):
            connection = relationentry.relationentry
            connections.extend([[tag.strip() for tag in connection.split(";")]])
        return connections

    def _all_sh_connections(self, instance) -> dict:
        return {
            "primary": self._prepare_connection(instance, "work_connection_primary"),
            "secondary": self._prepare_connection(
                instance, "work_connection_secondary"
            ),
            "sh_connection_type": self._prepare_connection(
                instance, "sh_connection_type"
            ),
        }

    def parse_connections(self, instance, data):
        all_connections = self._all_sh_connections(instance)
        # Init element lists

        data["individual_connections"] = []
        data["work_connections"] = []
        data["source_connections"] = []
        data["text_connections"] = []
        data["performance_connections"] = []

        for connection_key in all_connections.keys():
            connections = all_connections[connection_key]
            for connection in connections:
                if connection and len(connection) > 0:
                    if connection[0].lower() == "individual":
                        data = self.parse_individual_connections(connection, data)
                    elif connection[0].lower() == "works":
                        data = self.parse_work_connections(connection, data)
        return data

    def parse_individual_connections(self, sh_connection, data):
        """ Parse all connections looking for indiviudal types"""
        if len(sh_connection) > 1:
            label = ""
            if sh_connection[1] == "Biographical" or sh_connection[1] == "Biography":
                # This is a biographical location
                if len(sh_connection) > 3:
                    label = "{} - {}".format(
                        sh_connection[2],
                        sh_connection[3],
                    )
                elif len(sh_connection) > 2:
                    label = "{}".format(sh_connection[2])
                elif len(sh_connection) > 1:
                    label = "{}".format(sh_connection[1])
            elif len(sh_connection) > 2:
                label = sh_connection[2]
            else:
                label = sh_connection[1]
            if label and len(label) > 0:
                data["individual_connections"].append(label)
        return data

    def parse_work_connections(self, sh_connection, data):
        """ Parse all connections looking for work types"""
        if len(sh_connection) > 1:
            label = sh_connection[1]
            if (
                sh_connection[1].lower() == "plays"
                or sh_connection[1].lower() == "poems"
            ):
                # if (len(sh_connection) > 3 and
                #     sh_connection[2].lower() == 'sonnets'
                # ):
                #     # Numbered sonnets
                #     label = '{}-{}'.format(
                #         sh_connection[2], sh_connection[3]
                #     )
                if len(sh_connection) > 2:
                    label = sh_connection[2]
                for split_label in label.split(","):
                    if len(split_label) > 0:
                        data["work_connections"].append(split_label.strip())

            elif sh_connection[1].lower() == "attributed to shakespeare":
                # create type using type of attributed work

                label = sh_connection[2]

                data["work_connections"].append(label)

            # Texts
            elif sh_connection[1].lower() == "text":
                if len(sh_connection) > 3:
                    if sh_connection[3] == "Translation":
                        label = sh_connection[3]
                    elif sh_connection[3] == "Portrait":
                        label = "Character - Portrait"
                    elif sh_connection[3] == "Identification":
                        label = "Character - Identification"
                elif len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                if len(label) > 0:
                    data["text_connections"].append(label)

            elif sh_connection[1].lower() == "performance":
                if len(sh_connection) > 3:
                    if sh_connection[3] == "Portrait":
                        if (
                            len(sh_connection) > 4
                            and sh_connection[4] == "Actor portrait"
                        ):
                            label = "Character - Actor Portrait"
                        else:
                            label = "Character - Portrait"
                    elif sh_connection[3] == "Identification":
                        label = "Character - Identification"
                elif len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                if len(label) > 0:
                    data["performance_connections"].append(label)

            # Sources
            elif sh_connection[1].lower() == "sources":
                if len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                if len(label) > 0:
                    data["source_connections"].append(label)
        return data

    def prepare_related_material(self, instance):
        for related in instance.relatedmaterial_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(related.relatedmaterial)
            )
            for element in root.xpath("//span[@class='ead-archref']"):
                return element.text
        return ""

    def prepare_connection_primary(self, instance):
        return self._prepare_connection(instance, "work_connection_primary")

    def prepare_connection_secondary(self, instance):
        return self._prepare_connection(instance, "work_connection_secondary")

    def prepare_connection_type(self, instance):
        return self._prepare_connection(instance, "sh_connection_type")

    def prepare_creators(self, instance):
        """Return object field data for creators of `instance`.

        Since the data is potentially drawn from multiple models, and
        when used as a facet we get only the value of the single facet
        field, store the pk and model name to be used as the facet
        field, so that the display value can be looked up.

        """
        creators = []
        for origination in instance.origination_set.all():
            for name_type in ("corpname", "famname", "name", "persname"):
                for name in getattr(origination, name_type + "_set").all():
                    creators.append(
                        {
                            "key": "{}-{}".format(name_type, name.id),
                            "name": name.assembled_name,
                        }
                    )
        return creators

    @classmethod
    def _prepare_control_access_data(cls, instance, path):
        data = []
        for controlaccess in instance.controlaccess_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(controlaccess.controlaccess)
            )
            for element in root.xpath(path):
                data.append(element.text.strip())
        return data

    def _get_donors(self, instance):
        return EADDocument._prepare_control_access_data(
            instance,
            "span[@class='ead-persname'][@data-ead-relator='donor']/span["
            "@class='ead-part']",
        )

    def _get_acquirers(self, instance):
        return EADDocument._prepare_control_access_data(
            instance,
            "span[@class='ead-persname'][@data-ead-relator='acquirer']/span["
            "@class='ead-part']",
        )

    def _get_publishers(self, instance):
        return EADDocument._prepare_control_access_data(
            instance,
            "span[@class='ead-persname']["
            "@data-ead-relator='publisher']/span[@class='ead-part']",
        )

    def prepare_related_people(self, instance):
        return {
            "acquirers": self._get_acquirers(instance),
            "donors": self._get_donors(instance),
            "publishers": self._get_publishers(instance),
        }

    def prepare_related_sources(self, instance):
        data = self.parse_connections(instance, {})

        return {
            "individuals": data["individual_connections"],
            "works": data["work_connections"],
            "texts": data["text_connections"],
            "sources": data["source_connections"],
            "performances": data["performance_connections"],
        }

    def prepare_date_of_acquisition(self, instance):
        return self._get_year_range(instance, "acquisition")

    def prepare_date_of_creation(self, instance):
        return self._get_year_range(instance, "creation")

    def prepare_notes(self, instance):
        # From ScopeContent.scopecontent with localtype="notes".
        scope_contents = instance.scopecontent_set.filter(localtype="notes")
        notes = " ".join(scope_contents.values_list("scopecontent", flat=True))
        return {"raw": notes, "html": notes}

    def prepare_provenance(self, instance):
        # From CustodHist.custodhist
        provenances = []
        for prov in instance.custodhist_set.all():
            raw = prov.custodhist
            html = prov.custodhist
            try:
                root = etree.fromstring(prov.custodhist)
                raw = root.text.strip()
            except etree.XMLSyntaxError:
                pass
            # <p class="ead-p">None</p>
            html = EADDocument._strip_initial_p(html)

            provenances.append({"raw": raw, "html": html})

        if len(provenances) > 0 and provenances[0]["html"] != "None":
            return provenances[0]
        return {"raw": "", "html": ""}

    @classmethod
    def _strip_initial_p(cls, html):
        """Strip p tag wrapping provenence, leave others intact"""
        html = re.sub("^<p.*?>", "", html)
        html = re.sub("</p>$", "", html)
        return html

    def prepare_references_published(self, instance):
        # From Bibliography.bibliography
        refs = " ".join(
            instance.bibliography_set.values_list("bibliography", flat=True)
        )

        html_refs = re.sub("^<.*?>", "", refs)
        html_refs = re.sub("</.*?>$", "", html_refs)
        if html_refs == "None" or html_refs == '<span class="ead-bibref">None</span>':
            # blank null value
            refs = ""
            html_refs = ""
        return {"raw": refs, "html": html_refs}

    def prepare_references_unpublished(self, instance):
        # From SourceEntry.sourceentry
        entries = SourceEntry.objects.filter(source__sources=instance)
        refs = " ".join(entries.values_list("sourceentry", flat=True))
        if len(refs) > 0:
            if refs == "None":
                # blank null value
                refs = ""
        return {"raw": refs, "html": refs}

    def prepare_unittitle(self, instance):
        try:
            title = instance.unittitle_set.all()[0].unittitle
        except IndexError:
            title = "[No title]"
        return title
