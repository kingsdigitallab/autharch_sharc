from django.db import models


class SharcIIIF(models.Model):
    """
    IIIF image records from the RCT spreadsheet
    """

    iiif_uri = models.CharField(blank=True, null=True, max_length=512)
    rcin = models.CharField(blank=True, null=True, max_length=256)
    images_available = models.TextField(blank=True, null=True)
    department = models.CharField(blank=True, null=True, max_length=256)
    order = models.IntegerField(default=1)
