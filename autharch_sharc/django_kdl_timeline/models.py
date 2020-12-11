"""
Timeline models
By KDL(EH) 17/7/2020

Django models to support the import, modification and serialisation
of timeline events into a JSON format usable by timelineJS3
https://timeline.knightlab.com/

A simplified version from FIELD without Dublin Core

Important Note: Snippets below are not registered by default
in case you want to subclass them.

"""
import json

from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.edit_handlers import (
    FieldPanel, FieldRowPanel,
    MultiFieldPanel,
    InlinePanel, HelpPanel)
from wagtail.core.models import (Page, Orderable)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.images.api.fields import ImageRenditionField
from wagtail.images.models import (Image)
from wagtail.search import index
from wagtail.api import APIField


class AbstractTimelineSlide(models.Model):
    """Event for Timeline_JS
    Based on JSON format:
    https://timeline.knightlab.com/docs/json-format.html
    """

    unique_id = models.CharField(max_length=256, blank=True)

    # Start and End dates
    start_date_year = models.IntegerField(null=False, blank=False, default=0)
    start_date_month = models.IntegerField(null=False, blank=False, default=0)
    start_date_day = models.IntegerField(null=False, blank=False, default=0)

    end_date_year = models.IntegerField(null=False, blank=False, default=0)
    end_date_month = models.IntegerField(null=False, blank=False, default=0)
    end_date_day = models.IntegerField(null=False, blank=False, default=0)

    # Text fields to display
    headline = models.TextField(blank=True, default='')
    text = models.TextField(blank=True, default='')

    ordering = ['start_date_year']

    def serialise_start_date(self):
        """Get only relevant start dates, return as dict"""
        dates = {"year": self.start_date_year,
                 "display_date": self.start_date_year}
        if self.start_date_month > 0:
            dates['month'] = self.start_date_month
        if self.start_date_day > 0:
            dates['day'] = self.start_date_day
        return dates

    def serialise_end_date(self):
        """Get only relevant start dates, return as dict"""
        dates = {"year": self.end_date_year}
        if self.end_date_month > 0:
            dates['month'] = self.end_date_month
        if self.end_date_day > 0:
            dates['day'] = self.end_date_day
        return dates

    def serialise_text(self):
        text = {}
        if len(self.headline) > 0:
            text['headline'] = self.headline
        if len(self.text) > 0:
            text['text'] = self.text
        return text

    def __str__(self):
        return '{}:{},{}"{}'.format(
            self.unique_id, self.start_date_year, self.headline, self.text
        )

    def get_timeline_data(self):
        """ Serialise object for timelineJS"""
        data = {'start_date': self.serialise_start_date(),
                'display_date': "{}".format(self.start_date_year),
                }
        if len(self.serialise_end_date()) > 0:
            data['end_date'] = self.serialise_end_date()
        if len(self.serialise_text()) > 0:
            data['text'] = self.serialise_text()
        if len(self.unique_id) > 0:
            data['unique_id'] = self.unique_id
        return data

    def to_timeline_json(self):
        return json.dumps(self.get_timeline_data())

    class Meta:
        abstract = True




"""
Implementation objects.  Current flavours are:

1. Pure Django with attached image object
2. Wagtail, with timeline index, slides as snippets, and wagtailimage

"""


class TimelineSlide(AbstractTimelineSlide):
    """Plain vanilla slide, mostly used for testing """
    pass


class TimelineSlideWithImage(AbstractTimelineSlide):
    """ 'Pure' django implementation with attached image """
    image = models.ImageField(null=True)


class AbstractTimelineEventSnippet(index.Indexed, AbstractTimelineSlide):
    class Meta:
        abstract = True

    panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel('start_date_year'),
                        FieldPanel('start_date_month'),
                        FieldPanel('start_date_day'),
                    ]
                ),
                FieldRowPanel([
                    FieldPanel('end_date_year'),
                    FieldPanel('end_date_month'),
                    FieldPanel('end_date_day'),
                ]),
            ],
            heading="Dates",
            classname="collapsible"
        ),
        FieldPanel('headline'),
        FieldPanel('text'),
    ]




search_fields = [
    index.SearchField('headline', partial_match=True),
    index.SearchField('text', partial_match=True),
]


class AbstractTimelinePage(Page):
    """ A wagtail rich text page wrapper for the timeline"""

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        return context

    class Meta:
        abstract = True


class TimelineEventWithImageSnippet(AbstractTimelineEventSnippet):
    image_rendition = 'width-400'
    thumb_rendition = 'width-50'

    image = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        blank=True, null=True
    )

    panels = AbstractTimelineEventSnippet.panels + [
        ImageChooserPanel('image')
    ]

    def get_timeline_data(self):
        data = super().get_timeline_data()
        if self.image:
            data['media'] = {'url': self.image.get_rendition(self.image_rendition).url,
                      'thumbnail': self.image.get_rendition(self.thumb_rendition).url, }
        return data



class TimelineEventWithImageItem(
    Orderable,
    TimelineEventWithImageSnippet
):
    page = ParentalKey(
        'django_kdl_timeline.TimelinePage',
        on_delete=models.CASCADE,
        related_name='related_events')

    api_fields = [
        APIField('headline'),
        APIField('text'),
        # Adds information about the source image (eg, title) into the API
        APIField('image'),
        # Adds a URL to a rendered thumbnail of the image to the API
        APIField('image_thumbnail',
                 serializer=ImageRenditionField('fill-100x100',
                                                source='image')),
    ]


class TimelinePage(Page):
    content_panels = Page.content_panels + [
        InlinePanel('related_events', label="Timeline Events"),
    ]

    api_fields = [
        APIField("related_events")
    ]

