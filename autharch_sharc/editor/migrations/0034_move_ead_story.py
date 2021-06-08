# Generated by Django 3.0.10 on 2021-06-07 15:23

from django.db import migrations
from ead.models import EAD

from autharch_sharc.editor.models import StoryObject, WagtailEADSnippet


def move_ead_snippets(apps, schema_editor):
    for story_object in StoryObject.objects.all():
        if story_object.ead:
            if WagtailEADSnippet.objects.filter(ead=story_object.ead).count() > 0:
                ead_snippet = WagtailEADSnippet.objects.filter(ead=story_object.ead)[0]
                story_object.ead_snippet = ead_snippet
                story_object.save()


class Migration(migrations.Migration):

    dependencies = [
        ("editor", "0033_storyobject_ead_snippet"),
    ]

    operations = [
        migrations.RunPython(move_ead_snippets),
    ]