from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from lxml import etree

from ead.constants import NS_MAP
from ead.models import EAD, UnitDateStructuredDateRange


@registry.register_document
class EADDocument(Document):
    creators = fields.ObjectField(
        properties={
            "key": fields.KeywordField(),
            "name": fields.TextField(),
        }
    )
    pk = fields.IntegerField(attr="id")
    archdesc_level = fields.KeywordField(attr='archdesc_level')
    category = fields.KeywordField()
    date_of_acquisition = fields.IntegerField()
    date_of_creation = fields.IntegerField()
    publicationstatus_value = fields.KeywordField()
    unittitle = fields.TextField()

    class Index:
        name = "editor"

    class Django:
        model = EAD
        fields = [
            "maintenancestatus_value",
            "recordid",
        ]

    def _get_year_from_date(self, date):
        try:
            year_end_index = date.index('-')
            year = int(date[:year_end_index])
        except ValueError:
            try:
                year = int(date)
            except ValueError:
                year = None
        return year

    def _get_year_range(self, instance, datechar):
        try:
            date_range = UnitDateStructuredDateRange.objects.get(
                parent__did=instance, parent__datechar=datechar)
        except UnitDateStructuredDateRange.DoesNotExist:
            return []
        start_year = self._get_year_from_date(date_range.fromdate_standarddate)
        end_year = self._get_year_from_date(date_range.todate_standarddate)
        if start_year is None:
            years = []
        elif end_year is None:
            years = [start_year]
        else:
            years = list(range(start_year, end_year + 1))
        return years

    def prepare_category(self, instance):
        categories = []
        for controlaccess in instance.controlaccess_set.all():
            root = etree.fromstring('<wrapper>{}</wrapper>'.format(
                controlaccess.controlaccess))
            categories.extend(
                [str(category) for category in root.xpath(
                    'e:genreform/e:part/text()', namespaces=NS_MAP)])
        return categories

    def prepare_creators(self, instance):
        """Return object field data for creators of `instance`.

        Since the data is potentially drawn from multiple models, and
        when used as a facet we get only the value of the single facet
        field, store the pk and model name to be used as the facet
        field, so that the display value can be looked up.

        """
        creators = []
        for origination in instance.origination_set.all():
            for name_type in ("corpnames", "famnames", "names", "persnames"):
                for name in getattr(origination, name_type).all():
                    creators.append(
                        {
                            "key": '{}-{}'.format(name_type, name.id),
                            "name": name.assembled_name,
                        }
                    )
        return creators

    def prepare_date_of_acquisition(self, instance):
        return self._get_year_range(instance, 'acquisition')

    def prepare_date_of_creation(self, instance):
        return self._get_year_range(instance, 'creation')

    def prepare_unittitle(self, instance):
        try:
            title = instance.unittitle_set.all()[0].unittitle
        except IndexError:
            title = "[No title]"
        return title
