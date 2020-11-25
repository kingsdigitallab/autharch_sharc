from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from ead.constants import NS_MAP
from ead.models import EAD, RelationEntry, UnitDateStructuredDateRange
from elasticsearch_dsl import normalizer
from lxml import etree

lowercase_sort_normalizer = normalizer(
    "lowercase_sort", filter=["lowercase", "asciifolding"]
)


@registry.register_document
class EADDocument(Document):

    class Index:
        name = "editor"

    class Django:
        model = EAD
        fields = [
            "maintenancestatus_value",
            "recordid",
        ]

    creators = fields.ObjectField(
        properties={
            "key": fields.KeywordField(),
            "name": fields.TextField(),
        }
    )
    pk = fields.IntegerField(attr="id")
    archdesc_level = fields.KeywordField(attr='archdesc_level')
    category = fields.KeywordField(
        fields={
            "lowercase": fields.KeywordField(
                normalizer=lowercase_sort_normalizer),
            "suggest": fields.CompletionField(),
        }
    )
    acquirer = fields.KeywordField(
        fields={
            "suggest": fields.CompletionField(),
        }
    )
    donor = fields.KeywordField(
        fields={
            "suggest": fields.CompletionField(),
        }
    )
    connection_primary = fields.KeywordField()
    connection_secondary = fields.KeywordField()
    individual_connections = fields.KeywordField()
    work_connections = fields.KeywordField()
    text_connections = fields.KeywordField()
    source_connections = fields.KeywordField()
    performance_connections = fields.KeywordField()

    related_material = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
        }
    )
    connection_type = fields.KeywordField()
    date_of_acquisition = fields.IntegerField()
    date_of_creation = fields.IntegerField()
    publicationstatus_value = fields.KeywordField()
    unittitle = fields.TextField(
        fields={
            "raw": fields.KeywordField(),
            "sort": fields.KeywordField(normalizer=lowercase_sort_normalizer),
            "suggest": fields.CompletionField(),
        }
    )

    # todo this is inefficient, refactor

    def prepare_individual_connections(self, instance):
        data = self.parse_connections(instance, {})
        return data['individual_connections']

    def prepare_work_connections(self, instance):
        data = self.parse_connections(instance, {})
        return data['work_connections']

    def prepare_text_connections(self, instance):
        data = self.parse_connections(instance, {})
        return data['text_connections']

    def prepare_source_connections(self, instance):
        data = self.parse_connections(instance, {})
        return data['source_connections']

    def prepare_performance_connections(self, instance):
        data = self.parse_connections(instance, {})
        return data['performance_connections']

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

    def _prepare_connection(self, instance, localtype):
        connections = []
        for relationentry in RelationEntry.objects.filter(
            relation__relations=instance, localtype=localtype):
            connection = relationentry.relationentry
            connections.extend([tag.strip() for tag in connection.split(';')])
        return connections

    def _all_sh_connections(self, instance) -> dict:
        return {
            'primary': self._prepare_connection(
                instance, 'work_connection_primary'
            ),
            'secondary': self._prepare_connection(
                instance,
                'work_connection_secondary'
            ),
            'sh_connection_type': self._prepare_connection(
                instance,
                'sh_connection_type'
            )
        }

    def parse_connections(self, instance, data):
        all_connections = self._all_sh_connections(instance)
        # Init element lists

        data['individual_connections'] = []
        data['work_connections'] = []
        data['source_connections'] = []
        data['text_connections'] = []
        data['performance_connections'] = []

        for connection_key in all_connections.keys():
            connection = all_connections[connection_key]
            if connection[0].lower() == 'individual':
                data = self.parse_individual_connections(connection, data)
            elif connection[0].lower() == 'works':
                data = self.parse_work_connections(connection, data)
        return data

    def parse_individual_connections(self, sh_connection, data):
        """ Parse all connections looking for indiviudal types"""
        if len(sh_connection) > 1:
            if (sh_connection[1] == 'Biographical'
                and len(sh_connection) > 3):
                # This is a biographical location
                label = "{} - {}".format(
                    sh_connection[2],
                    sh_connection[3],
                )
            elif len(sh_connection) > 2:
                label = sh_connection[2]
            else:
                label = sh_connection[1]
            print(label)
            data['individual_connections'].append(label)
        return data

    def parse_work_connections(self, sh_connection, data):
        """ Parse all connections looking for work types"""
        if len(sh_connection) > 1:
            label = sh_connection[1]
            if (sh_connection[1].lower() == 'plays' or
                sh_connection[1].lower() == 'poems'):
                if (len(sh_connection) > 3 and
                    sh_connection[2].lower() == 'sonnets'
                ):
                    # Numbered sonnets
                    label = '{}-{}'.format(
                        sh_connection[2], sh_connection[3]
                    )
                elif len(sh_connection) > 2:
                    label = sh_connection[2]
                print(label)
                data['work_connections'].append(label)

            elif (sh_connection[1].lower() ==
                  "attributed to shakespeare"):
                # create type using type of attributed work

                label = sh_connection[2]
                print(label)
                data['work_connections'].append(label)

            # Texts
            elif sh_connection[1].lower() == 'text':
                if len(sh_connection) > 3:
                    if sh_connection[3] == 'Translation':
                        label = sh_connection[3]
                    elif sh_connection[3] == 'Portrait':
                        label = 'Character - Portrait'
                    elif sh_connection[3] == 'Identification':
                        label = 'Character - Identification'
                elif len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                data['text_connections'].append(label)

            elif sh_connection[1].lower() == 'performance':
                if len(sh_connection) > 3:
                    if sh_connection[3] == 'Portrait':
                        if (len(sh_connection) > 4 and sh_connection[
                            4] == 'Actor portrait'):
                            label = 'Character - Actor Portrait'
                        else:
                            label = 'Character - Portrait'
                    elif sh_connection[3] == 'Identification':
                        label = 'Character - Identification'
                elif len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                data['performance_connections'].append(label)

            # Sources
            elif sh_connection[1].lower() == 'sources':
                if len(sh_connection) > 2:
                    label = sh_connection[2]
                else:
                    label = sh_connection[1]
                data['source_connections'].append(label)
        return data

    def prepare_related_material(self, instance):
        for related in instance.relatedmaterial_set.all():
            root = etree.fromstring(
                '<wrapper>{}</wrapper>'.format(related.relatedmaterial)
            )
            for element in root.xpath(
                '/e:archref',
                namespaces=NS_MAP
            ):
                return element.text
        return ''

    def prepare_connection_primary(self, instance):
        return self._prepare_connection(instance, 'work_connection_primary')

    def prepare_connection_secondary(self, instance):
        return self._prepare_connection(instance, 'work_connection_secondary')

    def prepare_connection_type(self, instance):
        return self._prepare_connection(instance, 'sh_connection_type')

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

    @classmethod
    def _prepare_control_access_data(cls, instance, path):
        data = []
        for controlaccess in instance.controlaccess_set.all():
            root = etree.fromstring(
                '<wrapper>{}</wrapper>'.format(controlaccess.controlaccess)
            )
            for element in root.xpath(
                path,
                namespaces=NS_MAP
            ):
                data.append(element.text.strip())
        return data

    def prepare_donor(self, instance):
        return EADDocument._prepare_control_access_data(
            instance, "e:persname[@relator='donor']/e:part")

    def prepare_acquirer(self, instance):
        return EADDocument._prepare_control_access_data(
            instance, "e:persname[@relator='acquirer']/e:part")

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
