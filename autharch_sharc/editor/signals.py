import django.dispatch
from django_elasticsearch_dsl.signals import BaseSignalProcessor

view_post_save = django.dispatch.Signal(providing_args=["instance"])


class ElasticsearchSemiRealTimeSignalProcessor(BaseSignalProcessor):
    """An Elasticsearch signal processor that is like the
    RealTimeSignalProcessor but does not connect the post_save signal,
    leaving handling of index updates to the new view_post_save
    signal.

    The need for this is due to the EAD model often not triggering a
    post_save signal because the changes are to related models.

    """

    def setup(self):
        view_post_save.connect(self.handle_save)

    def teardown(self):
        view_post_save.disconnect(self.handle_save)
