from django.test import RequestFactory, TestCase

from editor.documents import EADDocument


class EADDocumentTestCase(TestCase):
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

        for test_connection in self.test_connection_strings:
            connection = [tag.strip() for tag in test_connection.split(';')]
            if connection[0].lower() == 'individual':
                data = doc.parse_individual_connections(connection)

        self.assertEqual(len(data['individual_elements']), 2)


    def test_parse_work_connections(self):
        doc = EADDocument()
        doc.work_elements = []
        doc.source_elements = []
        doc.text_elements = []
        doc.performance_elements = []

        for test_connection in self.test_connection_strings:
            data = doc.parse_work_connections(
                [tag.strip() for tag in test_connection.split(';')])

        self.assertEqual(len(data['work_elements']), 7)
        self.assertEqual(len(data['text_elements']), 2)
        self.assertEqual(len(data['source_elements']), 1)
        self.assertEqual(len(data['performance_elements']), 2)
