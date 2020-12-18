from django.db import models
from django_kdl_timeline.models import AbstractTimelineEventSnippet
from editor.documents import EADDocument
from wagtail.admin.edit_handlers import FieldPanel
from wagtail.api import APIField
from wagtail.core.fields import RichTextField
from wagtail.core.models import Page
from wagtail.search import index
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
            # Query the documents for document with RCIN
            rcin_search = EADDocument.search().query("match", reference=self.RCIN)
            response = rcin_search.execute()
            for h in response:
                # Use the media object from there to get image/thumbnail
                data["media"] = {
                    "title": self.headline,
                    "link": "/objects/{}".format(self.RCIN),
                    "url": h.media[0].full_image_url,
                    "thumbnail": h.media[0].thumbnail_url,
                }
                # Currently use the first media object we get
                # may need to change
                break

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


class RichTextPage(Page):
    body = RichTextField(blank=True, null=True)

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    subpage_types = ["RichTextPage"]

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("body"),
    ]

    api_fields = [
        APIField("title"),
        APIField("body"),
    ]

    promote_panels = Page.promote_panels
