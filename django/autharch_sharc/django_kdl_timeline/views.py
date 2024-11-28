# Create your views here.

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TimelineEventWithImageSnippet


class ListTimelineEvents(APIView):
    """
    Return events as JSON for async requests
    """

    model = TimelineEventWithImageSnippet

    def get_events(self, request):
        """
        Get events based on http request
        Add them to the current context
        :param request:request with filter args
        :return: queryset of FieldTimelineEvent objects
        """

        # get event objects
        events = self.model.objects.all()
        # Add filtering
        if "category" in request.GET:
            if len(request.GET["category"]) > 0:
                events.filter(category__category_name=request.GET["category"])
        return events

    def events_to_slides(self, events):
        """Convert a FieldTimelineEvent object queryset into a list of
        slides using FieldTimelineEvent.get_timeline_data()
        :return: list of dicts for timeline slides
        """
        slides = list()
        for event in events:
            slides.append(event.get_timeline_data())
        return slides

    def get(self, request, *args, **kwargs):
        events = self.get_events(request)
        slides = list()
        if events:
            slides = self.events_to_slides(events)
        timeline = {"events": slides}
        return Response(timeline)
