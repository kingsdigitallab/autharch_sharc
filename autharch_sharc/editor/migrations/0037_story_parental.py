# Generated by Django 3.0.10 on 2021-06-08 10:53

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("editor", "0036_ead_snippet_theme"),
    ]

    operations = [
        migrations.AlterField(
            model_name="storyobject",
            name="story",
            field=modelcluster.fields.ParentalKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="story_objects",
                to="editor.StoryObjectCollection",
            ),
        ),
    ]