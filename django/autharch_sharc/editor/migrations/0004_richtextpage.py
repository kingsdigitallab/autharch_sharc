# Generated by Django 3.0.10 on 2020-12-18 12:06

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):
    dependencies = [
        ('wagtailcore', '0059_apply_collection_ordering'),
        ('editor', '0003_timeline_ordering'),
    ]

    operations = [
        migrations.CreateModel(
            name='RichTextPage',
            fields=[
                ('page_ptr', models.OneToOneField(
                    auto_created=True,
                    on_delete=django.db.models.deletion.CASCADE,
                    parent_link=True,
                    primary_key=True,
                    serialize=False,
                    to='wagtailcore.Page')),
                ('body',
                 wagtail.core.fields.RichTextField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]