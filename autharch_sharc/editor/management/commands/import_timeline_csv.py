import argparse
import csv
from typing import Iterator

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.db.utils import DataError
from editor.models import SharcTimelineEventSnippet


class Command(BaseCommand):
    help = 'Import timeline events from csv. Inherit this, don\'t run directly'
    verbose = 1  # show logging on screen

    min_row_length = 5
    events_created = 0
    events_updated = 0
    event_links = {}

    def parse_event_csv_line(self, csv_line) -> None:
        # check for event id
        if len(csv_line) >= self.min_row_length and len(csv_line[1]) > 0:
            # Date, Creator, Title, RCIN, Blurb
            start_year = int(csv_line[0])
            event, created = SharcTimelineEventSnippet.objects.get_or_create(
                RCIN=csv_line[3],
                creator=csv_line[1],
                headline=csv_line[2],
                text=csv_line[4],
                start_date_year=start_year
            )

    def attach_events_to_default_timeline(self) -> None:
        pass

    def handle(self, *args, **options):
        # import rights tab
        csvfile = csv.reader(
            options['csvfile'], delimiter=',')

        # Import events
        x = 0
        for csv_line in csvfile:
            self.parse_event_csv_line(csv_line)
            x += 1
            print("{}\n".format(x))

        self.attach_events_to_default_timeline()

        # Add event links
        self.stdout.write("{} Events created, {} updated".format(
            self.events_created,
            self.events_updated
        ))
