from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from ead.models import EAD


@registry.register_document
class EADDocument(Document):
    creators = fields.ObjectField(
        properties={
            "pk": fields.IntegerField(),
            "name": fields.TextField(),
        }
    )
    # there's an automatically created field called _id
    pk = fields.IntegerField(attr="id")
    unittitle = fields.TextField()

    class Index:
        name = "editor"

    class Django:
        model = EAD
        fields = [
            "archdesc_level",
            "maintenancestatus_value",
            "publicationstatus_value",
            "recordid",
        ]

    def prepare_creators(self, instance):
        creators = []
        for origination in instance.origination_set.all():
            for name_type in ("corpnames", "famnames", "names", "persnames"):
                for name in getattr(origination, name_type).all():
                    creators.append(
                        {
                            "pk": name.id,
                            "name": "".join(
                                name.part_set.values_list("plain_name", flat=True)
                            ),
                        }
                    )
        return creators

    def prepare_unittitle(self, instance):
        try:
            title = instance.unittitle_set.all()[0].unittitle
        except IndexError:
            title = "[No title]"
        return title
