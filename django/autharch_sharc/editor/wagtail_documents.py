from django_elasticsearch_dsl.registries import registry

from autharch_sharc.editor.models import SharcRichTextPage, StreamFieldPage

from .documents import EADDocument


@registry.register_document
class WagtailSharcRichTextPageDocument(EADDocument):
    """Document to merge wagtail pages into other documents for
    site search"""

    class Django:
        model = SharcRichTextPage
        fields = ["id", "title", "slug"]

    @classmethod
    def generate_id(cls, object_instance):
        """
        Overloaded to stop conflicts with ead documents
        """
        return object_instance.pk + 10000

    def get_queryset(self):
        """
        Only index live documents
        """
        return self.django.model._default_manager.all().live()

    def prepare(self, instance):
        body = instance.body

        if instance.last_published_at is not None:
            date_of_creation = instance.last_published_at.year
        else:
            date_of_creation = 0
        data = {
            "pk": instance.pk,
            "unittitle": instance.title,
            "body": body,
            "date_of_creation": date_of_creation,
            "category": instance._meta.object_name,
            "reference": instance.slug,
            "doc_type": "page",
            "size": "",
            "medium": "",
            "label": "",
            "creators": [],
            "place_of_origin": "",
            "date_of_acquisition": "",
            "related_material": [],
            "related_sources": [],
            "related_people": [],
            "media": [],
        }
        data["search_content"] = self.get_search_content(data) + body
        return data


@registry.register_document
class WagtailStreamFieldPageDocument(EADDocument):
    """Document to merge wagtail pages into other documents for
    site search"""

    class Django:
        model = StreamFieldPage
        fields = ["id", "title", "slug"]

    @classmethod
    def generate_id(cls, object_instance):
        """
        Overloaded to stop conflicts with ead documents
        """
        return object_instance.pk + 10000

    def get_queryset(self):
        """
        Only index live documents
        """
        return self.django.model._default_manager.all().live()

    def prepare(self, instance):
        body = ""
        body_blocks = instance.body
        for block in body_blocks:
            body += str(block)
        try:
            date_of_creation = instance.last_published_at.year
        except AttributeError:
            date_of_creation = None
        data = {
            "pk": instance.pk,
            "unittitle": instance.title,
            "body": body,
            "date_of_creation": date_of_creation,
            "category": instance._meta.object_name,
            "reference": instance.slug,
            "doc_type": "page",
            "size": "",
            "medium": "",
            "label": "",
            "creators": [],
            "place_of_origin": "",
            "date_of_acquisition": "",
            "related_material": [],
            "related_sources": [],
            "related_people": [],
            "media": [],
        }
        data["search_content"] = self.get_search_content(data) + body
        return data
