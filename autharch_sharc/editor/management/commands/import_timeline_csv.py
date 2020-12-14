import argparse
import csv

from django.core.management.base import BaseCommand
from editor.models import SharcTimelineEventSnippet


class Command(BaseCommand):
    help = "Import timeline events from csv."
    verbose = 1  # show logging on screen

    min_row_length = 5
    events_created = 0
    events_updated = 0
    event_links = {}

    def add_arguments(self, parser) -> None:
        # csv file to parse
        parser.add_argument("csvfile", type=argparse.FileType("r"))

    def parse_event_csv_line(self, csv_line) -> None:
        # check for event id
        if len(csv_line) >= self.min_row_length and len(csv_line[1]) > 0:
            # Date, Creator, Title, RCIN, Blurb
            try:
                start_year = int(csv_line[0])
                event, created = SharcTimelineEventSnippet.objects.get_or_create(
                    RCIN=csv_line[3],
                    creator=csv_line[1],
                    headline=csv_line[2],
                    text=csv_line[4],
                    start_date_year=start_year,
                )
                if created:
                    self.events_created += 1
                else:
                    self.events_updated += 1
            except ValueError:
                pass

    def attach_events_to_default_timeline(self) -> None:
        pass

    def handle(self, *args, **options):
        # import rights tab
        csvfile = csv.reader(options["csvfile"], delimiter=",")

        # Import events
        x = 0
        for csv_line in csvfile:
            if "Date" not in csv_line[0]:
                self.parse_event_csv_line(csv_line)
            x += 1
            print("{}\n".format(x))

        self.attach_events_to_default_timeline()

        # Add event links
        self.stdout.write(
            "{} Events created, {} updated".format(
                self.events_created, self.events_updated
            )
        )
