import requests
from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from ead.constants import NS_MAP
from ead.models import (
    EAD,
    DIdPhysDescStructuredDimensions,
    RelationEntry,
    UnitDateStructuredDateRange,
)
from elasticsearch_dsl import normalizer
from lxml import etree

lowercase_sort_normalizer = normalizer(
    "lowercase_sort", filter=["lowercase", "asciifolding"]
)
from editor.models import RichTextPage, StreamFieldPage

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
        "label"
    )


@registry.register_document
class EADDocument(Document):
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
    category = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
            "lowercase": fields.KeywordField(normalizer=lowercase_sort_normalizer),
            "suggest": fields.CompletionField(),
        }
    )
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

    search_content = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
            "sort": fields.KeywordField(normalizer=lowercase_sort_normalizer),
        }
    )

    def prepare_doc_type(self, instance):
        return "object"

    def prepare_search_content(self, instance):
        """ Deliberately empty so we can instantiate this at
        the end in prepare"""
        return ""

    def get_search_content(self, data):
        """ Run after all other fields prepared to ensure
        fields are populated"""
        content = ''
        for field in eaddocument_search_fields:
            if field in data:
                content = content + ' ' + str(data[field])
        return content

    def prepare(self, instance):
        data = super().prepare(instance)
        data['search_content'] = self.get_search_content(data)
        return data



    def prepare_media(self, instance):
        """
        This is a placeholder for now
        will add live data when we get it

        "iiif_manifest_url": "https://rct.resourcespace.com/iiif/732115a/",
            "iiif_image_url":
            "https://rct.resourcespace.com/iiif/image/34658/info.json",
            "thumbnail_url": "https://rct.resourcespace.com/iiif/image/34658
            /full/thm/0/default.jpg"

            https://rct.resourcespace.com/iiif/234/
        """

        media = []
        # Temporary defaults so we have data for the frontend
        iiif_manifest_url = "/rct/iiif/732115a/"
        full_image_url = (
            "https://rct.resourcespace.com/iiif/image/34658/full/max/0/default.jpg"
        )
        iiif_image_url = "/rct/iiif/image/34658"
        thumbnail_url = (
            "https://rct.resourcespace.com/iiif/image/34658/full/thm/0/default.jpg"
        )
        image_width = 4015
        image_height = 2980
        thumbnail_width = 175
        thumbnail_height = 130
        label = "1"
        # Try to fetch the iiif manifest
        RCIN = self.prepare_reference(instance)
        manifest_url = "https://rct.resourcespace.com/iiif/{}/".format(RCIN)
        r = requests.get(manifest_url)
        if r.status_code == 200 and len(r.text) > 0:
            # It's there, parse it
            response = r.json()
            # print(manifest_url)

            try:
                if "sequences" in response and len(response["sequences"]) > 0:
                    iiif_manifest_url = manifest_url
                    for canvas in response["sequences"][0]["canvases"]:
                        if "label" in canvas:
                            label = canvas["label"]
                        image = canvas["images"][0]
                        # Full size image
                        full_image_url = image["resource"]["@id"]
                        iiif_image_url = image["resource"]["service"]["@id"]
                        iiif_image_url = iiif_image_url.replace(
                            "https://rct.resourcespace.com/", "/rct"
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
                        "e:genreform/e:part/text()", namespaces=NS_MAP
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
        categories = []
        for controlaccess in instance.controlaccess_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(controlaccess.controlaccess)
            )
            categories.extend(
                [
                    str(category)
                    for category in root.xpath(
                        "e:genreform/e:part/text()", namespaces=NS_MAP
                    )
                ]
            )
        if len(categories) > 0:
            return categories[0]
        return ""

    def _prepare_connection(self, instance, localtype):
        connections = []
        for relationentry in RelationEntry.objects.filter(
            relation__relations=instance, localtype=localtype
        ):
            connection = relationentry.relationentry
            connections.extend([tag.strip() for tag in connection.split(";")])
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
            connection = all_connections[connection_key]
            if connection and len(connection) > 0:
                if connection[0].lower() == "individual":
                    data = self.parse_individual_connections(connection, data)
                elif connection[0].lower() == "works":
                    data = self.parse_work_connections(connection, data)
        return data

    def parse_individual_connections(self, sh_connection, data):
        """ Parse all connections looking for indiviudal types"""
        if len(sh_connection) > 1:
            if sh_connection[1] == "Biographical" and len(sh_connection) > 3:
                # This is a biographical location
                label = "{} - {}".format(
                    sh_connection[2],
                    sh_connection[3],
                )
            elif len(sh_connection) > 2:
                label = sh_connection[2]
            else:
                label = sh_connection[1]

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
                data["performance_connections"].append(label)

            # Sources
            elif sh_connection[1].lower() == "sources":
                if len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                data["source_connections"].append(label)
        return data

    def prepare_related_material(self, instance):
        for related in instance.relatedmaterial_set.all():
            root = etree.fromstring(
                "<wrapper>{}</wrapper>".format(related.relatedmaterial)
            )
            for element in root.xpath("/e:archref", namespaces=NS_MAP):
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
            for name_type in ("corpnames", "famnames", "names", "persnames"):
                for name in getattr(origination, name_type).all():
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
            for element in root.xpath(path, namespaces=NS_MAP):
                data.append(element.text.strip())
        return data

    def _get_donors(self, instance):
        return EADDocument._prepare_control_access_data(
            instance, "e:persname[@relator='donor']/e:part"
        )

    def _get_acquirers(self, instance):
        return EADDocument._prepare_control_access_data(
            instance, "e:persname[@relator='acquirer']/e:part"
        )

    def _get_publishers(self, instance):
        return EADDocument._prepare_control_access_data(
            instance, "e:persname[@relator='publisher']/e:part"
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

    def prepare_unittitle(self, instance):
        try:
            title = instance.unittitle_set.all()[0].unittitle
        except IndexError:
            title = "[No title]"
        return title


@registry.register_document
class WagtailRichTextPageDocument(EADDocument):
    """Document to merge wagtail pages into other documents for
    site search"""

    class Django:
        model = RichTextPage
        fields = ["id", "title", "slug"]

    @classmethod
    def generate_id(cls, object_instance):
        """
        Overloaded to stop conflicts with ead documents
        """
        return object_instance.pk+10000

    def get_queryset(self):
        """
        Only index live documents
        """
        return self.django.model._default_manager.all().live()

    def prepare(self, instance):
        body = instance.body

        if instance.last_published_at is not None:
            date_of_creation = instance.last_published_at.year
        else:
            date_of_creation = 0
        data = {
            "pk": instance.pk,
            "unittitle": instance.title,
            "body": body,
            "date_of_creation": date_of_creation,
            "category": instance._meta.object_name,
            "reference": instance.slug,
            "doc_type": "page",
            "size": "",
            "medium": "",
            "label": "",
            "creators": [],
            "place_of_origin": "",
            "date_of_acquisition": "",
            "related_material": [],
            "related_sources": [],
            "related_people": [],
            "media": [],
        }
        data['search_content'] = self.get_search_content(data) + body
        return data


@registry.register_document
class WagtailStreamFieldPageDocument(EADDocument):
    """Document to merge wagtail pages into other documents for
    site search"""


    class Django:
        model = StreamFieldPage
        fields = ["id", "title", "slug"]

    @classmethod
    def generate_id(cls, object_instance):
        """
        Overloaded to stop conflicts with ead documents
        """
        return object_instance.pk + 10000

    def get_queryset(self):
        """
        Only index live documents
        """
        return self.django.model._default_manager.all().live()

    def prepare(self, instance):
        body = ""
        body_blocks = instance.body
        for block in body_blocks:
            body += str(block)
        try:
            date_of_creation = instance.last_published_at.year
        except AttributeError:
            date_of_creation = None
        data = {
            "pk": instance.pk,
            "unittitle": instance.title,
            "body": body,
            "date_of_creation": date_of_creation,
            "category": instance._meta.object_name,
            "reference": instance.slug,
            "doc_type": "page",
            "size": "",
            "medium": "",
            "label": "",
            "creators": [],
            "place_of_origin": "",
            "date_of_acquisition": "",
            "related_material": [],
            "related_sources": [],
            "related_people": [],
            "media": [],
        }
        data['search_content'] = self.get_search_content(data) + body
        return data
