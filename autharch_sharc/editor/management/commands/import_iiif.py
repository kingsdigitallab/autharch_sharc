import csv
import re

from django.core.management.base import BaseCommand

from autharch_sharc.editor.models import SharcIIIF


class Command(BaseCommand):
    help = "Import iiif_urls in csv."
    verbose = 1  # show logging on screen

    min_row_length = 5
    events_created = 0
    events_updated = 0
    event_links = {}

    # def add_arguments(self, parser) -> None:
    #     # csv file to parse
    #     parser.add_argument("csvfile", type=argparse.FileType("r"))

    def parse_iiif_row(self, csv_line, column_format, department="") -> None:
        """Parse the various sheets of the manifests,
        looking for IIIF uris.
        column_format is a dict of which columns contain primary/secondary
        uris, as well as metadata if present
        """
        # check for event id
        if len(csv_line) > 0:
            # Date, Creator, Title, RCIN, Blurb
            """
            iiif_uri = models.CharField(blank=True, null=True, max_length=512)
            rcin = models.CharField(blank=True, null=True, max_length=256)
            images_available = models.TextField(blank=True, null=True)
            department = models.CharField(blank=True, null=True, max_length=256)
            """
            # todo will populate this once format of sheet is more clear

            if "iiif_uri" in column_format:
                rcin = ""
                if "images_available" in column_format:
                    images_available = csv_line[column_format["images_available"]]
                else:
                    images_available = ""
                for uri_column in column_format["iiif_uri"]:
                    iiif_uri = csv_line[uri_column]
                    # pdb.set_trace()
                    if len(iiif_uri) > 0 and "http" in iiif_uri:
                        if len(rcin) == 0:
                            # get the end of the uri
                            # use first column as the rcin
                            rcin_pattern = re.compile(r"https://.*/(.*)/\n*$")
                            result = rcin_pattern.search(iiif_uri)
                            if result:

                                rcin = result.group(1)

                        if len(iiif_uri) > 0 and "https" in iiif_uri and len(rcin) > 0:
                            try:
                                event, created = SharcIIIF.objects.get_or_create(
                                    rcin=rcin,
                                    iiif_uri=iiif_uri,
                                    images_available=images_available,
                                    department=department,
                                )
                                if created:
                                    self.events_created += 1
                                else:
                                    self.events_updated += 1
                                print("{}:{}\n".format(rcin, iiif_uri))
                            except ValueError:
                                pass

    def parse_iiif_sheet(self, filename, column_format, department) -> None:
        with open(filename, "r") as csv_file:
            csvfile = csv.reader(csv_file, delimiter=",")
            for csv_line in csvfile:
                self.parse_iiif_row(csv_line, column_format, department)

    def handle(self, *args, **options):
        # Reset objects
        SharcIIIF.objects.all().delete()
        # import sheets
        self.parse_iiif_sheet(
            "data/ShaRC_manifests_March2021_library.csv",
            {"images_available": 2, "iiif_uri": [3, 4, 5, 6, 7]},
            "Library",
        )

        self.parse_iiif_sheet(
            "data/ShaRC_manifests_March2021_paintings.csv",
            {"images_available": 2, "iiif_uri": [3, 4, 5]},
            "Paintings",
        )

        self.parse_iiif_sheet(
            "data/ShaRC_manifests_March2021_printroom.csv",
            {"images_available": 2, "iiif_uri": [3, 4, 5]},
            "Print Room",
        )

        self.stdout.write(
            "{} URIs created, {} updated".format(
                self.events_created, self.events_updated
            )
        )
