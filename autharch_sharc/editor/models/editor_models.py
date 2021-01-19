from django.db import models


class EADObjectGroup(models.Model):
    """ Group of ead objects e.g. theme"""
    title = models.TextField(null=True, blank=True)
    slug = models.CharField(null=True, blank=True, max_length=128)
    introduction = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class EADObject(models.Model):
    """ Contains just the RCIN rather than foreign key
    to allow rebuilding of documents without deleting data"""
    RCIN = models.CharField(null=True, blank=True, max_length=128)
    ead_group = models.ForeignKey(
        'EADObjectGroup',
        on_delete=models.CASCADE,
        null=True
    )
