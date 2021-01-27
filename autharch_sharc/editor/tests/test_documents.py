import pytest

from django.test import RequestFactory, TestCase
from autharch_sharc.editor.documents import EADDocument


class TestEADDocument:
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

    def test_parse_individual_connections(self):
        doc = EADDocument()
        doc.individual_elements = []
        data = {
            "individual_connections": list()
        }
        for test_connection in self.test_connection_strings:
            connection = [tag.strip() for tag in test_connection.split(';')]
            if connection[0].lower() == 'individual':
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
                [tag.strip() for tag in test_connection.split(';')], data)

        assert len(data["work_connections"]) == 7
        assert len(data["text_connections"]) == 2
        assert len(data["source_connections"]) == 1
        assert len(data["performance_connections"]) == 2

    # def prepare_themes(self, instance):

    # def prepare_doc_type(self, instance):

    #
    # def prepare_search_content(self, instance):
    #
    # def get_search_content(self, data):
    #
    # def prepare(self, instance):
    #
    #
    #
    # def prepare_media(self, instance):

