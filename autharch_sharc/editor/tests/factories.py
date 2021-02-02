import ead.models as ead_models
import factory
from factory.django import DjangoModelFactory

import autharch_sharc.editor.models as models


class EADObjectFactory(DjangoModelFactory):
    RCIN = factory.Faker("random_int", min=1, max=9999)

    class Meta:
        model = models.EADObject


class EADObjectGroupFactory(DjangoModelFactory):
    """ Group of ead objects e.g. theme"""

    title = factory.Faker("sentence", nb_words=4)
    slug = factory.Faker("slug")
    introduction = factory.Faker("sentence", nb_words=6)
    description = factory.Faker("sentence", nb_words=8)

    class Meta:
        model = models.EADObjectGroup


class EADFactory(DjangoModelFactory):
    class Meta:
        model = ead_models.EAD


class PhysDescSetPhysDescStructuredFactory(DjangoModelFactory):
    class Meta:
        model = ead_models.PhysDescSetPhysDescStructured
