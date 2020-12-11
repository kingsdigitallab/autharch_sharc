from django_kdl_timeline.models import AbstractTimelineEventSnippet
from wagtail.snippets.models import register_snippet
from django.db import models


class SharcTimelineEventSnippet(AbstractTimelineEventSnippet):
    """ Events imported from csv for Sharc
    Fields in csv: Date,Creator,Title,RCIN,Blurb
    Title to headline
    Blurb to text
    """
    RCIN = models.TextField(null=True, blank=True)
    creator = models.TextField(null=True, blank=True)

    def get_timeline_data(self):
        data = super().get_timeline_data()
        if self.RCIN:
            """ Use the manifests from RCT here
            Will need refactoring after more data received
            Match to manifest by RCIN when ready"""
            data['media'] = {}
        return data


register_snippet(SharcTimelineEventSnippet)
