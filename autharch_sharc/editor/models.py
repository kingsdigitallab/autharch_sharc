from django.db import models
from django_kdl_timeline.models import AbstractTimelineEventSnippet
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.snippets.models import register_snippet


class SharcTimelineEventSnippet(AbstractTimelineEventSnippet):
    """Events imported from csv for Sharc
    Fields in csv: Date,Creator,Title,RCIN,Blurb
    Title to headline
    Blurb to text
    """

    RCIN = models.TextField(null=True, blank=True)
    creator = models.TextField(null=True, blank=True)

    def get_timeline_data(self):
        data = super().get_timeline_data()
        if self.RCIN:
            data["unique_id"] = self.RCIN
            """ Use the manifests from RCT here
            Will need refactoring after more data received
            Match to manifest by RCIN when ready"""
            data["media"] = {
                "link": "/objects/{}".format(self.RCIN),
                "thumbnail": "https://rct.resourcespace.com/iiif/image/{"
                "}/full/thm/0/default.jpg".format(self.RCIN),
            }
        return data

    panels = AbstractTimelineEventSnippet.panels + [
        FieldPanel("RCIN"),
        FieldPanel("creator"),
    ]

    class Meta:
        verbose_name = "Timeline event"
        verbose_name_plural = "Timeline events"
        ordering = ["start_date_year"]

    def __str__(self):
        return "{}:{} (RCIN {})".format(self.start_date_year, self.headline, self.RCIN)


register_snippet(SharcTimelineEventSnippet)
