from typing import Tuple

from django.core.management.base import BaseCommand
from ead.models import EAD

from autharch_sharc.editor import models


def add_themes() -> Tuple[int, int, int]:
    """ Default Themes from partner spreadsheet """

    shakespeare, created = models.Theme.objects.get_or_create(
        title="William Shakespeare",
        slug="group_william_shakespeare",
        description="",
    )

    on_the_stage, created = models.Theme.objects.get_or_create(
        title="On the Stage",
        slug="group_stage",
        description="",
    )

    on_the_page, created = models.Theme.objects.get_or_create(
        title="On the Page",
        slug="group_page",
        description="",
    )

    shakespeare_rcin = ["661421", "40497", "406072", "447173.a"]
    stage_rcin = ["913000", "655013", "2913567", "GEO/MAIN/55462"]
    page_rcin = ["1059072", "813725", "1008125", "MED/16/1/6"]

    shakespeare_attached = 0
    page_attached = 0
    stage_attached = 0

    """
    If default rcins are present, attach objects to themes
    """
    for rcin in page_rcin:

        for ead_object in EAD.objects.filter(unitid__unitid=rcin):
            on_the_page.ead_objects.add(ead_object)
            page_attached += 1

    for rcin in shakespeare_rcin:

        for ead_object in EAD.objects.filter(unitid__unitid=rcin):
            shakespeare.ead_objects.add(ead_object)
            shakespeare_attached += 1

    for rcin in stage_rcin:

        for ead_object in EAD.objects.filter(unitid__unitid=rcin):
            on_the_stage.ead_objects.add(ead_object)
            stage_attached += 1
    return page_attached, shakespeare_attached, stage_attached


class Command(BaseCommand):
    help = "Import timeline events from csv."

    def handle(self, *args, **options):
        page_attached, shakespeare_attached, stage_attached = add_themes()

        # Add event links
        self.stdout.write(
            "Themes loaded: Shakespeare - {}, stage - {}, page - {}".format(
                shakespeare_attached, stage_attached, page_attached
            )
        )
