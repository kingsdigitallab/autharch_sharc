import glob
import os

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from lxml import etree

from ead.constants import NS_MAP
from ead.models import EAD, Relation, RelationEntry


class Command(BaseCommand):
    help = "Re-imports sh_connection items from specified XML, overwriting existing connections."

    def add_arguments(self, parser):
        parser.add_argument("xml_dir", metavar="DIR",
                            help="Directory containing XML to import.")

    @transaction.atomic
    def handle(self, *args, **options):
        parser = etree.XMLParser(ns_clean=True, remove_blank_text=True)
        xml_pattern = os.path.join(options["xml_dir"], "*.xml")
        for xml_path in glob.glob(xml_pattern):
            self.reimport_file(xml_path, parser)

    def reimport_file(self, xml_path, parser):
        """Reimport connections from EAD3 XML file at `xml_path`."""
        self.stdout.write("Re-importing file at {}.".format(xml_path))
        tree = etree.parse(xml_path, parser=parser)
        ead = tree.getroot()
        recordid = ead.xpath("e:control/e:recordid/text()",
                             namespaces=NS_MAP)[0]
        try:
            record = EAD.objects.get(recordid=recordid)
        except EAD.DoesNotExist:
            raise CommandError(
                "Record with record ID {} does not exist.".format(recordid))
        self.stdout.write("Deleting existing connections.")
        for relation in record.relation_set.filter(
                otherrelationtype="sh_connection"):
            relation.delete()
        for relation_el in ead.xpath("e:archdesc/e:relations/e:relation[@otherrelationtype='sh_connection']", namespaces=NS_MAP):
            relation = Relation(
                relations=record, relationtype="otherrelationtype",
                otherrelationtype="sh_connection")
            relation.save()
            for entry_el in relation_el.xpath('e:relationentry',
                                              namespaces=NS_MAP):
                entry = RelationEntry(
                    relation=relation, relationentry=entry_el.text,
                    localtype=entry_el.get("localtype"))
                entry.save()
