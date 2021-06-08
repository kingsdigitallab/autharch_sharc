import kdl_wagtail.core.blocks as kdl_blocks
from django.db import models
from ead.models import EAD
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel,
    HelpPanel,
    InlinePanel,
    StreamFieldPanel,
)
from wagtail.api import APIField
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.core.templatetags.wagtailcore_tags import RichText
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.search import index
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.snippets.models import register_snippet

from autharch_sharc.django_kdl_timeline.models import AbstractTimelineEventSnippet
from autharch_sharc.editor.documents import EADDocument
from autharch_sharc.editor.serializers import EADDocumentResultSerializer

from .stream_blocks import APIRichTextBlock, RichTextNoParagraphBlock


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
        api_values = super().get_api_representation(value, context)
        if "image" in value and value["image"] is not None:
            image = value["image"]
            api_values["filename"] = image.filename
            api_values["full_url"] = image.get_rendition(self.full_rendition).url
            api_values["full_width"] = image.get_rendition(self.full_rendition).width
            api_values["full_height"] = image.get_rendition(self.full_rendition).height
        # "id": value.pk,
        return api_values

    @classmethod
    def image_to_api(cls, value: dict, api_values: dict):
        if "image" in value and value["image"] is not None:
            image = value["image"]
            api_values["filename"] = image.filename
            api_values["full_url"] = image.get_rendition(cls.full_rendition).url
            api_values["full_width"] = image.get_rendition(cls.full_rendition).width
            api_values["full_height"] = image.get_rendition(cls.full_rendition).height
        return api_values


class SharcImageGalleryBlock(kdl_blocks.GalleryBlock):
    def get_api_representation(self, value, context=None):
        api_values = []
        if "images_block" in value:
            for image_block in value["images_block"]:
                api_value = {
                    "transcription": str(image_block["transcription"]),
                    "description": str(image_block["description"]),
                    "caption": image_block["caption"],
                    "attribution": image_block["attribution"],
                    "page": image_block["page"],
                    "url": image_block["url"],
                    "alignment": image_block["alignment"],
                }

                api_value = ResourceImageBlock.image_to_api(image_block, api_value)
                api_values.append(api_value)

        return api_values


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
            ("paragraph", APIRichTextBlock()),
            ("image", ResourceImageBlock()),
            ("gallery", SharcImageGalleryBlock()),
            ("page", ResourcePageBlock()),
            ("document", ResourceDocumentBlock(icon="doc-full-inverse")),
            ("embed", ResourceEmbedBlock(icon="media")),
            ("table", TableBlock()),
            (
                "two_column_section",
                blocks.ListBlock(
                    blocks.StructBlock(
                        [
                            (
                                "heading",
                                RichTextNoParagraphBlock(classname="column-heading"),
                            ),
                            (
                                "subheading",
                                RichTextNoParagraphBlock(
                                    required=False, classname="column-subheading"
                                ),
                            ),
                            ("body", APIRichTextBlock(classname="column-body")),
                        ]
                    ),
                    classname="two-column-50-50",
                ),
            ),
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


class WagtailEADSnippet(index.Indexed, models.Model):
    """A middleware snippet to facilitate using the ead objects
    in wagtail
    Fields in the EAD for searching/filtering are brought forward here
    so wagtail can use them.
    Should be updated whenever the index is updated
    """

    ead = models.ForeignKey(
        EAD, null=True, on_delete=models.CASCADE, related_name="ead_snippets"
    )
    unittitle = models.TextField(null=True, blank=True)
    reference = models.CharField(max_length=256, null=True, blank=True)

    @property
    def search_content(self):
        return str(self.reference)

    panels = [
        HelpPanel(content="Do not Edit!"),
        FieldPanel("unittitle"),
        FieldPanel("reference"),
    ]

    search_fields = [
        index.SearchField("search_content", partial_match=True),
    ]

    class Meta:
        verbose_name = "EAD wagtail object"
        verbose_name_plural = "EAD wagtail objects"

    def __str__(self):
        label = str(self.reference) + ": " + str(self.unittitle)
        return (label[0:75] + "...") if len(label) > 75 else label


register_snippet(WagtailEADSnippet)


class StoryObjectCollection(StreamFieldPage):
    @property
    def related_documents(self):
        """NOTE: This arrangement is slightly round the houses
        because we
        A) need to preserve the fundamental relationships in the editor
        and
        B) need to return the elastic document, not the EAD object itself
        So the editor assigned the relationship, we build it into the index
        and then retrieve it as a doc as necessary
        """
        pks = []
        for story_object in self.story_objects.all():
            pks.append(story_object.ead_snippet.ead_id)
        s = EADDocument.search().filter("terms", pk=pks)
        related_documents = list()
        for hit in s:
            related_documents.append(EADDocumentResultSerializer(hit).data)
        return related_documents

    api_fields = [APIField("title"), APIField("body"), APIField("related_documents")]

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        InlinePanel("story_objects", label="Story Objects"),
    ]


class ThemeObjectCollection(StreamFieldPage):
    """ A collection of objects based on theme """

    ead_objects = models.ManyToManyField(EAD, related_name="themes")

    @property
    def related_documents(self):

        pks = []
        for theme_object in self.theme_objects.all():
            pks.append(theme_object.ead_snippet.ead_id)
        s = EADDocument.search().filter("terms", pk=pks)
        related_documents = list()
        for hit in s:
            related_documents.append(EADDocumentResultSerializer(hit).data)
        return related_documents

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        InlinePanel("theme_objects", label="Objects"),
    ]

    api_fields = [APIField("title"), APIField("body"), APIField("related_documents")]


class StoryObjectCollectionType(models.Model):
    type = models.CharField(blank=True, null=True, max_length=512)

    class Meta:
        verbose_name = "Story Connection Type"
        verbose_name_plural = "Story Connection Types"

    def __str__(self):
        return str(self.type)


register_snippet(StoryObjectCollectionType)


class ThemeObject(models.Model):
    """Intersection set for collections
    now including type
    """

    ead_snippet = models.ForeignKey(
        WagtailEADSnippet,
        null=True,
        on_delete=models.CASCADE,
        related_name="theme_snippet",
    )

    theme = ParentalKey(
        ThemeObjectCollection,
        related_name="theme_objects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Theme object"
        verbose_name_plural = "Theme objects"

    panels = [
        SnippetChooserPanel("ead_snippet"),
        FieldPanel("theme"),
    ]

    def __str__(self):
        label = str(self.story) + ":" + str(self.ead)
        return (label[0:75] + "...") if len(label) > 75 else label


register_snippet(ThemeObject)


class StoryObject(models.Model):
    """Intersection set for collections
    now including type
    """

    ead = models.ForeignKey(
        EAD, null=True, on_delete=models.CASCADE, related_name="story_objects"
    )

    ead_snippet = models.ForeignKey(
        WagtailEADSnippet,
        null=True,
        on_delete=models.CASCADE,
        related_name="story_snippet",
    )

    connection_type = models.ForeignKey(
        StoryObjectCollectionType, null=True, on_delete=models.CASCADE
    )

    story = ParentalKey(
        StoryObjectCollection,
        related_name="story_objects",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    class Meta:
        verbose_name = "Story object"
        verbose_name_plural = "Story objects"

    panels = [
        SnippetChooserPanel("ead_snippet"),
        FieldPanel("connection_type"),
        FieldPanel("story"),
    ]

    def __str__(self):
        label = str(self.story) + ":" + str(self.ead)
        return (label[0:75] + "...") if len(label) > 75 else label


register_snippet(StoryObject)
