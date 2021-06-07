import ead.models as ead_models
import factory
from factory.django import DjangoModelFactory

import autharch_sharc.editor.models as models


class StoryObjectFactory(DjangoModelFactory):
    RCIN = factory.Faker("random_int", min=1, max=9999)

    class Meta:
        model = models.StoryObject


class ThemeObjectCollectionFactory(DjangoModelFactory):
    """ Group of ead objects e.g. theme"""

    title = factory.Faker("sentence", nb_words=4)
    slug = factory.Faker("slug")
    body = "[]"
    live = True
    show_in_menus = True
    path = "00010009"
    depth = 2

    class Meta:
        model = models.ThemeObjectCollection


class EADFactory(DjangoModelFactory):
    class Meta:
        model = ead_models.EAD


class PhysDescSetPhysDescStructuredFactory(DjangoModelFactory):
    class Meta:
        model = ead_models.PhysDescSetPhysDescStructured
