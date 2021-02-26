# Generated by Django 3.0.10 on 2021-02-26 15:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ead', '0001_initial'),
        ('editor', '0020_story_object'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='storyobject',
            options={'verbose_name': 'Story object', 'verbose_name_plural': 'Story objects'},
        ),
        migrations.AlterModelOptions(
            name='storyobjectcollectiontype',
            options={'verbose_name': 'Story Connection Type', 'verbose_name_plural': 'Story Connection Types'},
        ),
        migrations.AlterField(
            model_name='storyobjectcollection',
            name='story_objects',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='story', to='editor.StoryObject'),
        ),
        migrations.AlterField(
            model_name='themeobjectcollection',
            name='theme_objects',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='themes', to='ead.EAD'),
        ),
    ]
