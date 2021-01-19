from django.db import models
# from django_elasticsearch_dsl import Document, fields
# from django_elasticsearch_dsl.registries import registry
from django_kdl_timeline.models import AbstractTimelineEventSnippet
from elasticsearch_dsl import normalizer
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.api import APIField
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.templatetags.wagtailcore_tags import RichText
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from rest_framework.fields import CharField


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
            # response = EADDocument.search().query(
            #     "match", reference=self.RCIN)
            # for h in response:
            #     # Use the media object from there to get image/thumbnail
            #     data["media"] = {
            #         "title": self.headline,
            #         "link": "/objects/{}".format(self.RCIN),
            #         "url": h.media[0].full_image_url,
            #         "thumbnail": h.media[0].thumbnail_url,
            #     }
            #     # Currently use the first media object we get
            #     # may need to change
            #     break

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
        return "{}:{} (RCIN {})".format(
            self.start_date_year, self.headline, self.RCIN)


register_snippet(SharcTimelineEventSnippet)

"""
Block types for resource page
"""


class ResourceBlock(blocks.StructBlock):
    """ Abstract base block for other types"""

    heading = blocks.CharBlock(form_classname="full title")
    body = blocks.RichTextBlock()

    def get_api_representation(self, value, context=None):
        body = RichText(value.get("body").source)
        return {
            "heading": value.get("heading"),
            "body": body.source,
        }
        # wagtail_headless_preview
        # dict_list = []
        # for item in value:
        #     temp_dict = {
        #         'period_name': value.get("period_name"),
        #         'description': value.get("description"),
        #         'duration': value.get("duration"),
        #         'events': value.get('events')
        #     }
        #     print(value.get('events'))
        #     dict_list.append(temp_dict)
        #     return dict_list

    class Meta:
        abstract = True
        template = "editor/blocks/resource_block.html"


class ResourceDocumentBlock(DocumentChooserBlock):
    """ Block with a document e.g. pdf attached """

    def get_api_representation(self, value, context=None):
        api_values = super().get_api_representation(value)
        doc = value
        api_values["document"] = {
            "title": doc.title,
            "filename": doc.filename,
            "url": doc.url,
        }
        return api_values


class ResourceImageBlock(ImageChooserBlock):
    """ Resource with image attached"""


    # todo rendition width?
    full_rendition = "width-1000"

    def get_api_representation(self, value, context=None):
        # api_values = super().get_api_representation(value)
        image = value
        api_values = {
            "id": value.pk,
            "filename": image.filename,
            "full_url": image.get_rendition(self.full_rendition).url,
            "full_width": image.get_rendition(self.full_rendition).width,
            "full_height": image.get_rendition(self.full_rendition).height,
        }
        return api_values


class ResourceEmbedBlock(EmbedBlock):
    """ Resource with embed attached"""

    def get_api_representation(self, value, context=None):
        return {
            "html": value.html,
            "url": value.url
        }


class ResourcePageBlock(blocks.PageChooserBlock):
    pass


class StreamFieldPage(Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title")),
            ('paragraph', blocks.RichTextBlock()),
            ("image", ResourceImageBlock()),
            ("page", ResourcePageBlock()),
            ("document", ResourceDocumentBlock(icon="doc-full-inverse")),
            ("embed", ResourceEmbedBlock(icon="media")),
        ]
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

    api_fields = [
        APIField("title"),
        APIField("body"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    promote_panels = Page.promote_panels


class RichTextPage(Page):
    body = RichTextField(blank=True, null=True)

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    subpage_types = ["RichTextPage", "StreamFieldPage"]

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("body"),
    ]

    def body_html(self):
        return str(RichText(self.body))

    api_fields = [
        APIField("title"),
        APIField("body"),
        APIField("body_html")
    ]

    promote_panels = Page.promote_panels

    def get_api_representation(self, value, context=None):
        """ Render the body as html for the frontend"""
        body = RichText(value.get("body").source)
        return {
            "title": value.get("title"),
            "body": body.source,
        }
