import kdl_wagtail.core.blocks as kdl_blocks
from django.db import models
from ead.models import EAD
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.api import APIField
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.templatetags.wagtailcore_tags import RichText
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from autharch_sharc.django_kdl_timeline.models import AbstractTimelineEventSnippet
from autharch_sharc.editor.serializers import EADDocumentResultSerializer

from .documents import EADDocument


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
        return "{}:{} (RCIN {})".format(self.start_date_year, self.headline, self.RCIN)


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

    class Meta:
        abstract = True
        template = "editor/blocks/resource_block.html"


class ResourceDocumentBlock(DocumentChooserBlock):
    """ Block with a document e.g. pdf attached """

    def get_api_representation(self, value, context=None):
        doc = value
        api_values = {
            "title": doc.title,
            "filename": doc.filename,
            "url": doc.url,
        }
        return api_values


class ResourceImageBlock(kdl_blocks.ImageBlock):
    """ Resource with image attached"""

    # todo rendition width?
    full_rendition = "width-1000"

    def get_api_representation(self, value, context=None):
        image = value
        api_values = {
            "id": value.pk,
            "filename": image.filename,
            "full_url": image.get_rendition(self.full_rendition).url,
            "full_width": image.get_rendition(self.full_rendition).width,
            "full_height": image.get_rendition(self.full_rendition).height,
        }
        return api_values


class SharcImageGalleryBlock(kdl_blocks.GalleryBlock):
    pass


class ResourceEmbedBlock(kdl_blocks.EmbedBlock):
    """ Resource with embed attached"""

    def get_api_representation(self, value, context=None):
        return {"html": value.html, "url": value.url}


class ResourcePageBlock(blocks.PageChooserBlock):
    pass


class StreamFieldPage(Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ResourceImageBlock()),
            ("gallery", SharcImageGalleryBlock()),
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


class SharcRichTextPage(Page):
    body = RichTextField(blank=True, null=True)

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    subpage_types = ["SharcRichTextPage", "StreamFieldPage"]

    content_panels = [
        FieldPanel("title", classname="full title"),
        FieldPanel("body"),
        FieldPanel("show_in_menus"),
    ]

    def body_html(self):
        return str(RichText(self.body))

    api_fields = [APIField("title"), APIField("body"), APIField("body_html")]

    promote_panels = Page.promote_panels

    def get_api_representation(self, value, context=None):
        """ Render the body as html for the frontend"""
        body = RichText(value.get("body").source)
        return {
            "title": value.get("title"),
            "body": body.source,
        }


class StoryObjectCollectionType(models.Model):
    type = models.CharField(blank=True, null=True, max_length=512)

    class Meta:
        verbose_name = "Story Connection Type"
        verbose_name_plural = "Story Connection Types"

    def __str__(self):
        return str(self.type)


class StoryObject(models.Model):
    """Intersection set for collections
    now including type"""

    ead_object = (
        models.ForeignKey(
            EAD, null=True, on_delete=models.CASCADE, related_name="story_objects"
        ),
    )
    connection_type = models.ForeignKey(
        StoryObjectCollectionType, null=True, on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = "Story object"
        verbose_name_plural = "Story objects"


register_snippet(StoryObject)
register_snippet(StoryObjectCollectionType)


class StoryObjectCollection(StreamFieldPage):
    story_objects = models.ForeignKey(
        StoryObject,
        related_name="story",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def related_documents(self):
        """NOTE: This arrangement is slightly round the houses
        because we
        A) need to preserve the fundamental relationships in the editor
        and
        B) need to return the elastic document, not the EAD object itself
        So the editor assigned the relationship, we build it into the index
        and then retrieve it as a doc as necessary
        """

        s = EADDocument.search().filter("term", stories__story=self.title)
        related_documents = list()
        for hit in s:
            related_documents.append(EADDocumentResultSerializer(hit).data)
        return related_documents

    api_fields = [
        APIField("title"),
        APIField("body"),
        APIField(
            "related_documents",
        ),
    ]


class ThemeObjectCollection(StreamFieldPage):
    """ A collection of objects based on theme """

    theme_objects = models.ForeignKey(
        EAD, related_name="themes", null=True, blank=True, on_delete=models.SET_NULL
    )

    def get_related_documents(self):
        s = EADDocument.search().filter("term", themes__raw=self.title)
        related_documents = list()
        for hit in s:
            related_documents.append(EADDocumentResultSerializer(hit).data)
        return related_documents

    api_fields = [
        APIField("title"),
        APIField("body"),
        APIField(
            "get_related_documents",
        ),
    ]
