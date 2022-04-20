from django.db import models


class RelatedMaterialParsed(models.Model):
    """Model to keep a master list of RCINs and
    whether the related material has been parsed after upload
    NOTE: Re-parse after save in editor
    """

    rcin = models.CharField(blank=True, null=True, max_length=256)
    parsed = models.BooleanField(default=False)
    related_material_parsed = models.TextField(blank=True, null=True)
