import csv

from django.core.management.base import BaseCommand

from autharch_sharc.editor.models import SharcIIIF


class Command(BaseCommand):
    help = "Import iiif_urls in csv."
    verbose = 1  # show logging on screen

    min_row_length = 5
    iif_created = 0
    events_updated = 0
    event_links = {}

    # def add_arguments(self, parser) -> None:
    #     # csv file to parse
    #     parser.add_argument("csvfile", type=argparse.FileType("r"))

    def parse_iiif_row(self, csv_line, column_format, last_rcin, department="") -> str:
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
                rcin = csv_line[0]
                if "images_available" in column_format:
                    images_available = csv_line[column_format["images_available"]]
                else:
                    images_available = ""
                if len(rcin) == 0 and len(last_rcin) > 0:
                    # Use RCIN from previous line
                    rcin = last_rcin
                if len(rcin) > 0:
                    for uri_column in column_format["iiif_uri"]:
                        iiif_uri = csv_line[uri_column]

                        if len(iiif_uri) > 0 and (
                            "http" in iiif_uri or "www" in iiif_uri
                        ):
                            if "http" not in iiif_uri:
                                # Add https at the front to make the link work
                                iiif_uri = "https://" + iiif_uri
                            # if len(rcin) == 0:
                            #     # get the end of the uri
                            #     # use first column as the rcin
                            #     rcin_pattern = re.compile(r"https://.*/(.*)/\n*$")
                            #     result = rcin_pattern.search(iiif_uri)
                            #     if result:
                            #
                            #         rcin = result.group(1)

                            if (
                                len(iiif_uri) > 0
                                and "https" in iiif_uri
                                and len(rcin) > 0
                            ):
                                try:
                                    order = 1
                                    # check if this rcin has been uploaded already
                                    # incrememnt order
                                    previous_uris = SharcIIIF.objects.filter(
                                        rcin=rcin
                                    ).order_by("order")
                                    if previous_uris.count() > 0:
                                        last = previous_uris.last()
                                        order = last.order + 1
                                    event, created = SharcIIIF.objects.get_or_create(
                                        rcin=rcin,
                                        iiif_uri=iiif_uri.strip(),
                                        images_available=images_available,
                                        department=department,
                                        order=order,
                                    )
                                    if created:
                                        self.iif_created += 1
                                    else:
                                        self.events_updated += 1
                                    print("{}:{}:{}\n".format(rcin, iiif_uri, order))
                                except ValueError:
                                    pass
                    return rcin
        return ""

    def parse_iiif_sheet(self, filename, column_format, department) -> None:
        with open(filename, "r") as csv_file:
            csvfile = csv.reader(csv_file, delimiter=",")
            print("{}\n".format(department))
            last_rcin = ""
            for csv_line in csvfile:
                last_rcin = self.parse_iiif_row(
                    csv_line, column_format, last_rcin, department
                )

    def handle(self, *args, **options):
        # Reset objects
        SharcIIIF.objects.all().delete()
        # import sheets
        totals = {}
        self.parse_iiif_sheet(
            "data/ShaRC_manifests_photographs.csv",
            {"images_available": 2, "iiif_uri": [3]},
            "Photographs",
        )
        totals["Photographs"] = self.iif_created
        self.iif_created = 0

        self.parse_iiif_sheet(
            "data/ShaRC_manifests_paintings.csv",
            {"images_available": 2, "iiif_uri": [3]},
            "Paintings",
        )
        totals["Paintings"] = self.iif_created
        self.iif_created = 0

        self.parse_iiif_sheet(
            "data/ShaRC_manifests_library.csv",
            {"images_available": 2, "iiif_uri": [3]},
            "Library",
        )
        totals["Library"] = self.iif_created
        self.iif_created = 0

        self.parse_iiif_sheet(
            "data/ShaRC_manifests_printroom.csv",
            {"images_available": 2, "iiif_uri": [3]},
            "Print Room",
        )
        totals["Print Room"] = self.iif_created
        self.iif_created = 0

        self.parse_iiif_sheet(
            "data/ShaRC_manifests_archives.csv",
            {"images_available": 2, "iiif_uri": [3]},
            "Archives",
        )
        totals["Archives"] = self.iif_created
        self.iif_created = 0
        grand_total = 0
        self.stdout.write("Complete.\n\nUpload totals: \n")
        for key, value in totals.items():
            self.stdout.write("{} - {}\n".format(key, value))
            grand_total += value
        self.stdout.write("\n Grand total - {}".format(grand_total))
