# Generated by Django 3.0.10 on 2021-06-07 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0032_ead_snippet_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='storyobject',
            name='ead_snippet',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ead_snippet', to='editor.WagtailEADSnippet'),
        ),
    ]
