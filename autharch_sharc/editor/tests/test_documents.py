# import ead.models as ead_models
import unittest.mock as mock

from ead.models import EAD

from autharch_sharc.editor.documents import EADDocument


class TestEADDocument:
    doc = EADDocument()
    test_rcin = "12345"
    test_connection_strings = [
        "None",
        "Individual; Biographical; Biographies",
        "Individual; Biographical; Locations; London",
        "Works; Text; Reading",
        "Works; Plays; As You Like It",
        "Works; Plays; The Taming of the Shrew",
        "Works; Plays; Twelfth Night",
        "Works; Plays; All's Well that Ends Well",
        "Works; Poems; Venus and Adonis",
        "Works; Attributed to Shakespeare; Apocrypha; Sir Thomas More",
        "Works; Attributed to Shakespeare; Forgeries",
        "Works; Text; Book",
        "Works; Sources; Book",
        "Works; Performance; Scene depiction",
        "Works; Performance; Performance record",
    ]

    def create_mock_instance(self):
        mock_unitid = mock.MagicMock()
        mock_unitid.unitid = self.test_rcin
        mock_instance = mock.MagicMock(spec=EAD)
        mock_instance.unitid_set.all = mock.Mock(return_value=[mock_unitid])
        return mock_instance

    # def test_prepare_size(self):
    #     import pdb
    #
    #     pdb.set_trace()
    #     mock_instance = self.create_mock_instance()
    #     mock_physdescstructured = mock.MagicMock(
    #     spec=DIdPhysDescStructuredDimensions)
    #     mock_physdescstructured.id = 1
    #     mock_physdescstructured.physdescstructuredtype = "spaceoccupied"
    #     mock_physdescstructured.quantity = "1"
    #     mock_physdescstructured.unittype = "item"
    #     mock_instance.physdescstructured_set.all = mock.Mock(
    #         return_value=[mock_physdescstructured]
    #     )
    #     size = self.doc.prepare_size(mock_instance)
    #     assert size == "1 item"

    def test_parse_individual_connections(self):
        doc = EADDocument()
        doc.individual_elements = []
        data = {"individual_connections": list()}
        for test_connection in self.test_connection_strings:
            connection = [tag.strip() for tag in test_connection.split(";")]
            if connection[0].lower() == "individual":
                data = doc.parse_individual_connections(connection, data)
        assert "individual_connections" in data
        assert len(data["individual_connections"]) == 2

    def test_parse_work_connections(self):
        doc = EADDocument()
        doc.work_elements = []
        doc.source_elements = []
        doc.text_elements = []
        doc.performance_elements = []
        data = {}
        data["individual_connections"] = []
        data["work_connections"] = []
        data["source_connections"] = []
        data["text_connections"] = []
        data["performance_connections"] = []

        for test_connection in self.test_connection_strings:
            data = doc.parse_work_connections(
                [tag.strip() for tag in test_connection.split(";")], data
            )

        assert len(data["work_connections"]) == 7
        assert len(data["text_connections"]) == 2
        assert len(data["source_connections"]) == 1
        assert len(data["performance_connections"]) == 2

    # @pytest.mark.django_db
    # def test_prepare_themes(self):
    #     import pdb
    #
    #     pdb.set_trace()
    #     doc = EADDocument()
    #     ead_1 = EADFactory()
    #     test_group_1 = ThemeObjectCollectionFactory()
    #     test_group_1.ead_objects.add(ead_1)
    #     # test_group_1.save()
    #     # StoryObjectFactory(RCIN="12345", ead_group=test_group_1)
    #     groups = doc.prepare_themes(ead_1)
    #
    #     assert len(groups) > 0
    #     # assert test_group_1.title in groups

    # def test_prepare_doc_type(self):
    #     assert self.doc.prepare_doc_type(self.doc) == self.doc.doc_type

    def test_get_search_content(self):
        data = {
            "unittitle": "A Title",
            "label": "Test",
            "related_sources.works": ["Hamlet"],
        }
        doc = EADDocument()
        content = doc.get_search_content(data)
        assert len(content) > 0
        assert content == " A Title ['Hamlet'] Test"

    # def prepare(self, instance):
    #
    #

    def test_prepare_reference(self):
        doc = EADDocument()
        mock_instance = self.create_mock_instance()
        rcin = doc.prepare_reference(mock_instance)
        assert rcin == self.test_rcin

    # def test_prepare_media(self):
    #     doc = EADDocument()
    #     mock_instance = self.create_mock_instance()
    #     mock_response = mock.MagicMock(spec=requests.Response)
    #     mock_response.status_code = 404
    #
    #     with mock.patch.object(
    #         requests, "get", return_value=mock_response
    #     ) as mock_method:
    #         # 404, not found, use default
    #         media = doc.prepare_media(mock_instance)
    #         assert len(media) > 0
    #         assert media[0]["iiif_manifest_url"] ==
    #         doc.default_iiif_manifest_url
    #         assert media[0]["full_image_url"] == doc.default_full_image_url
    #
    #         # 200, use returned data
    #         mock_response.status_code = 200
    #         test_manifest_json = json.load(
    #             open("autharch_sharc/editor/tests/test_iiif_data.json")
    #         )
    #         mock_response.json.return_value = test_manifest_json
    #         mock_response.text = str(test_manifest_json)
    #         mock_method.return_value = mock_response
    #         media = doc.prepare_media(mock_instance)
    #         assert len(media) > 0
    #         assert (
    #             media[0]["iiif_manifest_url"]
    #             == "https://rct.resourcespace.com/iiif/12345/"
    #         )
    #         assert media[0]["thumbnail_url"] == (
    #             "https://rct.resourcespace.com/iiif/image/52743"
    #             "/full/thm/0/default.jpg"
    #         )

    def test_prepare_place_of_origin(self):
        test_country = "Italy"
        mock_instance = self.create_mock_instance()
        mock_originalsloc = mock.MagicMock()
        mock_originalsloc.originalsloc = test_country
        mock_instance.originalsloc_set.all = mock.Mock(return_value=[mock_originalsloc])
        origins = self.doc.prepare_place_of_origin(mock_instance)
        assert len(origins) > 0
        assert test_country in origins

    """
    @pytest.mark.django_db



<physdescstructured coverage="whole" physdescstructuredtype="spaceoccupied">
                <quantity>1</quantity>
                <unittype>item</unittype>
                <dimensions>23.0 x 1.5 cm</dimensions>
            </physdescstructured>



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

    """
