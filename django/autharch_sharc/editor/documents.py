import re

import requests
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from ead.models import (
    EAD,
    DIdPhysDescStructuredDimensions,
    RelationEntry,
    SourceEntry,
    UnitDate,
    UnitDateStructuredDateRange,
)
from elasticsearch_dsl import analyzer, normalizer
from lxml import etree

from autharch_sharc.editor.models import SharcIIIF
from autharch_sharc.editor.models.related_material import RelatedMaterialParsed
from django.conf import settings

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
    "connection_primary",
    "label",
    "references_published",
    "references_unpublished",
    "related_people.all_people.name",
)

acquirer_aliases = [
    [
        "Queen Elizabeth (1900-2002), the Queen Mother",
        "Elizabeth (1900-2002), Duchess of York",
    ],
    [
        "King Edward VII (1841-1910), King of Great Britain and Ireland",
        "Prince Albert Edward (1841-1910), Prince of Wales",
        "Prince Albert Edward, Prince of Wales (1841-1910)",
    ],
    [
        "King George IV (1762-1830), King of Great Britain and Ireland",
        "Prince George (1762-1830), Prince of Wales",
        "Prince George (1762-1830), Prince Regent",
    ],
    [
        "King George V",
        "Prince George (1865-1936), Duke of York",
        "Prince George of Wales (1865-1936)",
    ],
    [
        "King George VI (1895-1952), King of Great Britain and Ireland",
        "Prince George, Duke of York (1895-1952)",
        "Prince Albert of Wales (1895-1952)",
    ],
    [
        "Queen Elizabeth II (b 1926), Queen of Great Britain and "
        "Northern "
        "Ireland",
        "Princess Elizabeth (b 1926), Duchess of Edinburgh",
        "Queen Elizabeth II (b. 1926), Queen of Great Britain and " "Northern Ireland",
    ],
    [
        "Queen Mary (1867-1953), consort of George V",
        "Princess May of Teck (1867-1953)",
        "Princess Mary, Princess of Wales",
        "Princess Mary (1867-1953), Princess of Wales",
        "Mary, Duchess of York",
    ],
    [
        "Queen Victoria (1819-1901), Queen of Great Britain and Ireland",
        "Princess Victoria (1786-1861), Duchess of Kent",
    ],
]


def find_links_in_material(related_material, parsed_material):
    for rmp in RelatedMaterialParsed.objects.all():
        matched_rcin = re.search(
            r"[\D|\s]+" + rmp.rcin + r"[\D|\s]+", " " + related_material + " "
        )
        if matched_rcin:
            # todo is this part of a range?
            matched_range = re.search(" " + rmp.rcin + r"-(\d+)", parsed_material)
            if matched_range is not None:
                upper_number = matched_range.group(1)
                upper_range = rmp.rcin[: -len(upper_number)] + upper_number
                related_material = related_material.replace(
                    rmp.rcin + "-" + upper_number, ""
                )
                parsed_material = parsed_material.replace("-" + upper_number, "")
                parsed_material = parsed_material.replace(
                    rmp.rcin,
                    '<a href="'
                    + settings.VUE_LIST_URL
                    + "?rcin__gte="
                    + rmp.rcin
                    + "&rcin__lte="
                    + upper_range
                    + '">'
                    + rmp.rcin
                    + "-"
                    + upper_range
                    + "</a>",
                )
            else:
                # Add link
                related_material = related_material.replace(rmp.rcin, "")
                parsed_material = parsed_material.replace(
                    rmp.rcin,
                    '<a href="'
                    + settings.VUE_DETAIL_URL
                    + rmp.rcin
                    + '">'
                    + rmp.rcin
                    + "</a>",
                )

    return parsed_material


def find_rcins_in_notes(related_material):
    """ Same process as below but for additional notes """
    # related_material = "A pen, ink and wash drawing of a tree identified
    # on the mount as 'Hern's [sic] Oak in Windsor Park mention'd in
    # Shakespear's Merry Wives of Windsor'. Several trees in the Great Park
    # have historically been connected with Herne's Oak, the tree that forms
    # the backdrop to the final scenes from The Merry Wives of Windsor,
    # and the Royal Collection has a sequence of prints showing both of the
    # primary candidates (RCINs 700443, 700760, 700761, 700772, 700775,
    # 700775, 700771, 503363, 700757, 700758, 700762, 700763, 700773,
    # 700774 and 700443). This drawing, by the Russian-born painter and
    # draughtsman Alexander Cozens, shows the 'first' tree to be given the
    # title, which was cut down on the orders of George III in 1796, having
    # ceased to vegetate (an order the king may later have regretted upon
    # realizing it was 'Herne's Oak'). Cozens shows it already dead."
    # "This drawing was presented to the Royal Collection in 1946 by E.
    # Horsman (or Horseman) Coles, and is one of several drawings to have
    # come from the same source - Horsman also donated several topographical
    # and view drawings to the British Museum around the same period. There
    # is no evidence that George VI took a particular interest in the
    # history of Herne's Oak, although five years after receiving this
    # drawing, in 1951, he presented one of the Royal Collection's two busts
    # of Shakespeare carved from the wood of the 'second' Herne's Oak to the
    # Windsor and Royal Borough Museum (see RCIN 7021)."
    parsed_material = related_material
    # Look for ALL RCINs in text field
    if len(related_material) > 0:
        parsed_material = find_links_in_material(related_material, parsed_material)
    return parsed_material


def find_rcins(rcin, related_material):
    """
    Due to the inconsistency of how references are written
    in the xml, I've had to brute force this and look for all
    rcins.
    2369159-84
    """

    parsed_material = related_material
    if RelatedMaterialParsed.objects.filter(rcin=rcin, parsed=True).count() > 0:
        # Parsed already return that
        rmp = RelatedMaterialParsed.objects.get(rcin=rcin, parsed=True)
        return rmp.related_material_parsed
    else:

        # Look for ALL RCINs in text field
        for rmp in RelatedMaterialParsed.objects.all():
            matched_rcin = re.search(
                r"[\D|\s]+" + rmp.rcin + r"[\D|\s]+", " " + related_material + " "
            )
            if matched_rcin:
                # todo is this part of a range?
                matched_range = re.search(" " + rmp.rcin + r"-(\d+)", parsed_material)
                if matched_range is not None:
                    upper_number = matched_range.group(1)
                    upper_range = rmp.rcin[: -len(upper_number)] + upper_number
                    related_material = related_material.replace(
                        rmp.rcin + "-" + upper_number, ""
                    )
                    parsed_material = parsed_material.replace("-" + upper_number, "")
                    parsed_material = parsed_material.replace(
                        rmp.rcin,
                        '<a href="'
                        + settings.VUE_LIST_URL
                        + "?rcin__gte="
                        + rmp.rcin
                        + "&rcin__lte="
                        + upper_range
                        + '">'
                        + rmp.rcin
                        + "-"
                        + upper_range
                        + "</a>",
                    )
                else:
                    # Add link
                    related_material = related_material.replace(rmp.rcin, "")
                    parsed_material = parsed_material.replace(
                        rmp.rcin,
                        '<a href="'
                        + settings.VUE_DETAIL_URL
                        + rmp.rcin
                        + '">'
                        + rmp.rcin
                        + "</a>",
                    )
        # add the result to the relatedmaterialparsed
        if RelatedMaterialParsed.objects.filter(rcin=rcin).count() > 0:
            related_material_parsed = RelatedMaterialParsed.objects.filter(rcin=rcin)[0]
        else:
            related_material_parsed = RelatedMaterialParsed(rcin=rcin)
        related_material_parsed.parsed = True
        related_material_parsed.related_material_parsed = parsed_material
        related_material_parsed.save()

    return parsed_material


@registry.register_document
class EADDocument(Document):
    """ Document model for EAD objects uploaded via xml"""

    """ Used for iiif images while we wait for them"""
    default_iiif_manifest_url = "PLACEHOLDER"
    default_full_image_url = "PLACEHOLDER"
    default_iiif_image_url = "PLACEHOLDER"
    default_thumbnail_url = "PLACEHOLDER"
    default_doc_type = "object"
    # Toggle for parsing related material
    # will be set to false if no RelatedMaterial objects
    do_parse_related = True

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
            "name": fields.KeywordField(),
        }
    )

    pk = fields.IntegerField(attr="id")
    reference = fields.KeywordField(fields={"text": fields.TextField()})
    rct_link = fields.KeywordField()
    rcin_numeric = fields.LongField()  # numeric field used for range matching
    # Has related material been parsed yet?
    related_material = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    related_material_parsed = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )

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
    # Added to show notes with links added
    notes_parsed = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    references_published = fields.ObjectField(
        properties={
            "reference": fields.TextField(
                fields={
                    "raw": fields.KeywordField(),
                }
            ),
        }
    )
    references_unpublished = fields.ObjectField(
        properties={
            "reference": fields.TextField(
                fields={
                    "raw": fields.KeywordField(),
                }
            ),
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
    #         "lowercase": fields.KeywordField(
    #         normalizer=lowercase_sort_normalizer),
    #     }
    # )
    related_people = fields.ObjectField(
        properties={
            "acquirers": fields.TextField(
                fields={
                    "raw": fields.KeywordField(),
                    "suggest": fields.CompletionField(),
                }
            ),
            "all_people": fields.ObjectField(
                properties={
                    "name": fields.TextField(
                        fields={
                            "raw": fields.KeywordField(),
                            "suggest": fields.CompletionField(),
                        }
                    ),
                    "surname": fields.KeywordField(),
                    "facet_label": fields.KeywordField(),
                    "type": fields.KeywordField(),
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
            "order": fields.IntegerField(),
        }
    )

    related_material = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    connection_type = fields.KeywordField()
    date_of_acquisition = fields.IntegerField()
    date_of_acquisition_range = fields.TextField()
    date_of_creation = fields.IntegerField()
    date_of_creation_range = fields.TextField()
    date_of_creation_notes = fields.TextField()
    date_of_acquisition_notes = fields.TextField()
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
    label = fields.KeywordField(
        fields={
            "text": fields.TextField(),
        }
    )
    doc_type = fields.KeywordField()
    is_visible = fields.BooleanField()

    search_content = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
            "sort": fields.KeywordField(normalizer=lowercase_sort_normalizer),
        }
    )

    def prepare_related_material_parsed(self, instance):

        return ""

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
    #     for story_object in StoryObject.objects.filter(
    #     ead_snippet__ead=instance):
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
        if self.do_parse_related and RelatedMaterialParsed.objects.count() == 0:
            print("No RelatedMaterial Records! Update after full index")
            self.do_parse_related = False
        elif self.do_parse_related and "related_material" in data:
            # Turned off as this material is no longer display on the site
            # parsed_material = find_rcins(data["reference"],
            # data["related_material"])
            data["related_material_parsed"] = data["related_material"]
            # print("{}\n".format(data["notes"]["html"]))
            parsed_notes = find_rcins_in_notes(data["notes"]["html"])
            data["notes_parsed"] = parsed_notes

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
        order = 1
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
                                        "https://rct.resourcespace.com/",
                                        "/rct/",
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

                                        media.append(
                                            {
                                                "label": canvas["label"],
                                                "iiif_manifest_url": iiif_manifest_url,
                                                "iiif_image_url": iiif_image_url,
                                                "full_image_url": full_image_url,
                                                "thumbnail_url": thumbnail_url,
                                                "image_width": image_width,
                                                "image_height": image_height,
                                                "thumbnail_width": thumbnail_width,
                                                "thumbnail_height": thumbnail_height,
                                                "order": order,
                                            }
                                        )
                                        order += 1
                        except IndexError:
                            pass
                except (
                    requests.exceptions.ConnectionError,
                    requests.exceptions.MissingSchema,
                ):
                    print("BaD url! {}\n".format(manifest_url))

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
        rcin = 0
        if len(instance.unitid_set.all()) > 0:
            rcin = [unitid.unitid for unitid in instance.unitid_set.all()][0]
            if len(rcin) > 0:
                if (
                    RelatedMaterialParsed.objects.filter(rcin=rcin).count() > 0
                    and RelatedMaterialParsed.objects.filter(
                        rcin=rcin, parsed=True
                    ).count()
                    > 0
                ):
                    rmp = RelatedMaterialParsed.objects.get(rcin=rcin)
                    rmp.related_material_parsed = ""
                    rmp.parsed = False
                    rmp.save()
                elif RelatedMaterialParsed.objects.filter(rcin=rcin).count() == 0:
                    rmp = RelatedMaterialParsed(rcin=rcin)
                    rmp.save()

        return rcin

    def prepare_rct_link(self, instance):
        """numerical link to RCT site
        Remove letters at the end of reference
        Remove ids that should not link to RCT
        """
        reference = ""
        if len(instance.unitid_set.all()) > 0:
            reference = [unitid.unitid for unitid in instance.unitid_set.all()][0]
        if reference not in [
            "1137279",
            "1167114",
            "1168390",
            "444107",
            "7021",
            "102755",
            "422463",
            "422464",
            "422527",
        ]:
            if re.search(r"^(\d+)\.\w+$", reference):
                result = re.search(r"^(\d+)\.\w+$", reference)
                return result.group(1)
            else:
                return reference
        return 0

    def prepare_rcin_numeric(self, instance):
        reference = ""
        if len(instance.unitid_set.all()) > 0:
            reference = [unitid.unitid for unitid in instance.unitid_set.all()][0]
        # Given the high amount of inconsistency I am ignoring records
        # with non-standard unit ids
        if "," in reference or ";" in reference:
            return 0
        # otherwise remove non-numbers
        rcin = re.sub("[^0-9]", "", reference)
        if len(rcin) == 0:
            rcin = "0"
        return int(rcin)

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

    def prepare_date_notes(self, instance, datechar):
        # <unitdate datechar="creation">Published December 3 1787</unitdate>
        for unitdate in UnitDate.objects.filter(did=instance, datechar=datechar):
            if unitdate.unitdate == "None":
                return None
            return unitdate.unitdate
        return None

    def prepare_date_of_creation_notes(self, instance):
        return self.prepare_date_notes(instance, "creation")

    def prepare_date_of_acquisition_notes(self, instance):
        return self.prepare_date_notes(instance, "acquisition")

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
            return str(root.xpath("span[@class='ead-genreform']/text()")[0]).strip()
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
            if label and len(label) > 0 and label not in data["individual_connections"]:
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
                    if (
                        len(split_label) > 0
                        and split_label not in data["work_connections"]
                    ):
                        data["work_connections"].append(split_label.strip())

            elif sh_connection[1].lower() == "attributed to shakespeare":
                # create type using type of attributed work

                label = sh_connection[2]
                if len(label) > 0 and label not in data["work_connections"]:
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
                if len(label) > 0 and label not in data["text_connections"]:
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
                if len(label) > 0 and label not in data["performance_connections"]:
                    data["performance_connections"].append(label)

            # Sources
            elif sh_connection[1].lower() == "sources":
                if len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                if len(label) > 0 and label not in data["source_connections"]:
                    data["source_connections"].append(label)
        return data

    def prepare_related_material(self, instance):
        related_material = ""
        for related in instance.relatedmaterial_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(related.relatedmaterial)
            )
            for element in root.xpath("//span[@class='ead-archref']"):
                if element.text is not None:
                    related_material = related_material + " \n " + element.text
        return related_material

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
                    if (
                        name
                        and name.assembled_name
                        and len(name.assembled_name.strip()) > 0
                    ):
                        creators.append(
                            {
                                "key": "{}-{}".format(name_type, name.id),
                                "name": name.assembled_name.strip(),
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

    def _get_acquirers(self, instance):
        return EADDocument._prepare_control_access_data(
            instance,
            "span[@class='ead-persname'][@data-ead-relator='acquirer']/span["
            "@class='ead-part']",
        )

    @classmethod
    def extract_surname(cls, name):
        """This is a bit of a hack to get a surname from heterogenous data
        we're getting the word before the () dates"""

        if re.search(r"\s+(\S+) \(.*?\)\s*", name):
            result = re.search(r"\s+(\S+) \(.*?\)\s*", name)
            return result.group(1)
        return ""

    @classmethod
    def get_people(cls, instance):
        # data-ead-relator
        people = list()
        path = "span[@class='ead-persname'][@data-ead-relator!='acquirer']"
        for controlaccess in instance.controlaccess_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(controlaccess.controlaccess)
            )

            for element in root.xpath(path):
                type = element.get("data-ead-relator")
                if len(element) > 0:
                    child = element[0]
                    name = child.text.strip()
                    if name is not None:
                        people.append(
                            {
                                "name": name,
                                "facet_label": "{} - {}".format(name, type),
                                "surname": cls.extract_surname(name),
                                "type": type,
                            }
                        )
                        # print("{} - {}\n".format(name, type))
        return people

    def prepare_related_people(self, instance):
        acquirers = self._get_acquirers(instance)
        all_acquirers = acquirers.copy()
        for acquirer in acquirers:

            # look for royal aliases above in acquirer
            for royal in acquirer_aliases:
                found = False
                alias_found = ""
                for royal_alias in royal:
                    if acquirer in royal_alias:
                        found = True
                        alias_found = royal_alias
                        acquirers.remove(acquirer)
                        print("{}\n".format(alias_found))
                        break
                if found:
                    # add aliases to acquirer
                    for royal_alias in royal:
                        if royal_alias != alias_found:
                            all_acquirers.append(royal_alias)

        people = EADDocument.get_people(instance)

        for creator in self.prepare_creators(instance):
            people.append(
                {
                    "name": creator["name"],
                    "facet_label": "{} - {}".format(creator["name"], "Creator"),
                    "surname": EADDocument.extract_surname(creator["name"]),
                    "type": "creator",
                }
            )

        return {
            "acquirers": all_acquirers,
            "all_people": people if len(people) > 0 else None,
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

    def prepare_date_of_acquisition_range(self, instance):
        return EADDocument._prepare_date_range(
            self._get_year_range(instance, "acquisition")
        )

    def prepare_date_of_creation(self, instance):
        return self._get_year_range(instance, "creation")

    def prepare_date_of_creation_range(self, instance):
        dates = self.prepare_date_of_creation(instance)
        return EADDocument._prepare_date_range(dates)

    @classmethod
    def _prepare_date_range(self, dates):
        if dates and len(dates) > 0:
            if len(dates) > 1:
                return "{}-{}".format(dates[0], dates[len(dates) - 1])
            return "{}".format(dates[0])
        return ""

    def prepare_notes(self, instance):
        # From ScopeContent.scopecontent with localtype="notes".
        scope_contents = instance.scopecontent_set.filter(localtype="notes")
        notes = " ".join(scope_contents.values_list("scopecontent", flat=True))
        # todo add rcin search here
        return {"raw": notes, "html": notes}

    def prepare_notes_parsed(self, instance):
        return ""

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
        raw = " ".join(instance.bibliography_set.values_list("bibliography", flat=True))

        # html_refs = re.sub("^<.*?>", "", refs)
        # html_refs = re.sub("</.*?>$", "", html_refs)
        refs = list()
        root = etree.fromstring("<wrapper>{}</wrapper>".format(raw))
        for child in root:
            # if len(html_refs) > 0:
            #     html_refs = html_refs + ", "

            if child.text is not None and child.text != "None":
                refs.append({"reference": child.text})

        return refs

    def prepare_references_unpublished(self, instance):
        # From SourceEntry.sourceentry
        entries = SourceEntry.objects.filter(source__sources=instance)
        # refs = " ".join(entries.values_list("sourceentry", flat=True))
        # if len(refs) > 0:
        #     if refs == "None":
        #         # blank null value
        #         refs = ""
        # return {"raw": refs, "html": refs}
        refs = list()
        for entry in entries:
            if entry.sourceentry != "None":
                refs.append({"reference": entry.sourceentry})
        return refs

    def prepare_unittitle(self, instance):
        try:
            title = instance.unittitle_set.all()[0].unittitle
        except IndexError:
            title = "[No title]"
        return title
