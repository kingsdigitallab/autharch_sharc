# Generated by Django 3.0.10 on 2021-03-01 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ead', '0001_initial'),
        ('editor', '0021_story_object_meta'),
    ]

    operations = [
        migrations.AddField(
            model_name='storyobject',
            name='ead',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='story_objects', to='ead.EAD'),
        ),
    ]
