# Generated by Django 3.0.10 on 2021-06-07 15:10

from django.db import migrations
from ead.models import EAD

from autharch_sharc.editor.documents import EADDocument
from autharch_sharc.editor.models import WagtailEADSnippet


def add_ead_snippets(apps, schema_editor):
    # save the object

    doc = EADDocument()
    # update the mirrored wagtail snippet
    for ead in EAD.objects.all():
        ead_snippet, created = WagtailEADSnippet.objects.get_or_create(
            unittitle=doc.prepare_unittitle(ead),
            reference=doc.prepare_reference(ead),
            ead=ead,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("editor", "0031_wagtail_ead_snippet"),
    ]

    operations = [
        migrations.RunPython(add_ead_snippets),
    ]
