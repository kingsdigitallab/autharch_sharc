import django.dispatch
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_elasticsearch_dsl.signals import BaseSignalProcessor
from ead.models import EAD

from autharch_sharc.editor.documents import EADDocument
from autharch_sharc.editor.models import WagtailEADSnippet

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


# @receiver(post_save, sender=StoryObject)
# @receiver(post_delete, sender=StoryObject)
# @receiver(post_save, sender=ThemeObjectCollection)
# @receiver(post_delete, sender=ThemeObjectCollection)
# def update_ead_index(sender, instance, **kwargs):
#     """Updates the related documents if one of the object stories/themes
#     have changed"""
#     ead_objects = []
#     if isinstance(instance, ThemeObjectCollection):
#         ead_objects = instance.theme_objects.all()
#     elif isinstance(instance, StoryObject):
#         ead_objects = instance.story_objects.all()
#
#     if ead_objects is not None and len(ead_objects) > 0:
#         for ead_object in ead_objects:
#             # Find related documents by unitid
#             s = (
#                 EADDocument.search()
#                 .filter("term", pk=ead_object.ead_snippet.ead_id)
#                 .execute()
#             )
#             for hit in s:
#                 # update index entry
#                 if isinstance(instance, ThemeObjectCollection):
#                     hit.themes = hit.prepare_themes(ead_object.ead_snippet.ead)
#                 elif isinstance(instance, StoryObject):
#                     hit.stories = hit.prepare_stories(ead_object.ead_snippet.ead)
#                 hit.save()


@receiver(post_save, sender=EAD)
def add_ead_snippetsave(sender, instance, **kwargs):
    # save the object
    doc = EADDocument()
    # update the mirrored wagtail snippet
    ead_snippet, created = WagtailEADSnippet.objects.get_or_create(
        unittitle=doc.prepare_unittitle(instance),
        reference=doc.prepare_reference(instance),
        ead=instance,
    )
