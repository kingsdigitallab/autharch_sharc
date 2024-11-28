# Generated by Django 3.0.10 on 2021-06-07 13:09

import django.db.models.deletion
import kdl_wagtail.core.blocks
import wagtail.contrib.table_block.blocks
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.embeds.blocks
import wagtail.images.blocks
import wagtail.search.index
from django.db import migrations, models

import autharch_sharc.editor.models.pages
import autharch_sharc.editor.models.stream_blocks


class Migration(migrations.Migration):

    dependencies = [
        ("ead", "0001_initial"),
        ("editor", "0030_sharciiif"),
    ]

    operations = [
        migrations.AlterField(
            model_name="streamfieldpage",
            name="body",
            field=wagtail.core.fields.StreamField(
                [
                    (
                        "heading",
                        wagtail.core.blocks.CharBlock(form_classname="full title"),
                    ),
                    (
                        "paragraph",
                        autharch_sharc.editor.models.stream_blocks.APIRichTextBlock(),
                    ),
                    (
                        "image",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "show_in_menus",
                                    wagtail.core.blocks.BooleanBlock(
                                        default=True, required=False
                                    ),
                                ),
                                (
                                    "transcription",
                                    kdl_wagtail.core.blocks.RichTextBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "description",
                                    kdl_wagtail.core.blocks.RichTextBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "attribution",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "caption",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "page",
                                    wagtail.core.blocks.PageChooserBlock(
                                        help_text="Link to a page", required=False
                                    ),
                                ),
                                (
                                    "url",
                                    wagtail.core.blocks.URLBlock(
                                        help_text="External link", required=False
                                    ),
                                ),
                                (
                                    "alignment",
                                    wagtail.core.blocks.ChoiceBlock(
                                        choices=[
                                            ("", "Select block alignment"),
                                            ("float-left", "Left"),
                                            ("float-right", "Right"),
                                            ("float-center", "Centre"),
                                            ("full-width", "Full width"),
                                        ]
                                    ),
                                ),
                                (
                                    "image",
                                    wagtail.images.blocks.ImageChooserBlock(
                                        required=True
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "gallery",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "show_in_menus",
                                    wagtail.core.blocks.BooleanBlock(
                                        default=True, required=False
                                    ),
                                ),
                                (
                                    "images_block",
                                    wagtail.core.blocks.ListBlock(
                                        wagtail.core.blocks.StructBlock(
                                            [
                                                (
                                                    "show_in_menus",
                                                    wagtail.core.blocks.BooleanBlock(
                                                        default=True, required=False
                                                    ),
                                                ),
                                                (
                                                    "transcription",
                                                    kdl_wagtail.core.blocks.RichTextBlock(
                                                        required=False
                                                    ),
                                                ),
                                                (
                                                    "description",
                                                    kdl_wagtail.core.blocks.RichTextBlock(
                                                        required=False
                                                    ),
                                                ),
                                                (
                                                    "attribution",
                                                    wagtail.core.blocks.CharBlock(
                                                        required=False
                                                    ),
                                                ),
                                                (
                                                    "caption",
                                                    wagtail.core.blocks.CharBlock(
                                                        required=False
                                                    ),
                                                ),
                                                (
                                                    "page",
                                                    wagtail.core.blocks.PageChooserBlock(
                                                        help_text="Link to a page",
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "url",
                                                    wagtail.core.blocks.URLBlock(
                                                        help_text="External link",
                                                        required=False,
                                                    ),
                                                ),
                                                (
                                                    "alignment",
                                                    wagtail.core.blocks.ChoiceBlock(
                                                        choices=[
                                                            (
                                                                "",
                                                                "Select block alignment",
                                                            ),
                                                            ("float-left", "Left"),
                                                            ("float-right", "Right"),
                                                            ("float-center", "Centre"),
                                                            (
                                                                "full-width",
                                                                "Full width",
                                                            ),
                                                        ]
                                                    ),
                                                ),
                                                (
                                                    "image",
                                                    wagtail.images.blocks.ImageChooserBlock(
                                                        required=True
                                                    ),
                                                ),
                                            ]
                                        )
                                    ),
                                ),
                            ]
                        ),
                    ),
                    ("page", autharch_sharc.editor.models.pages.ResourcePageBlock()),
                    (
                        "document",
                        autharch_sharc.editor.models.pages.ResourceDocumentBlock(
                            icon="doc-full-inverse"
                        ),
                    ),
                    (
                        "embed",
                        wagtail.core.blocks.StructBlock(
                            [
                                (
                                    "show_in_menus",
                                    wagtail.core.blocks.BooleanBlock(
                                        default=True, required=False
                                    ),
                                ),
                                (
                                    "transcription",
                                    kdl_wagtail.core.blocks.RichTextBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "description",
                                    kdl_wagtail.core.blocks.RichTextBlock(
                                        required=False
                                    ),
                                ),
                                (
                                    "attribution",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "caption",
                                    wagtail.core.blocks.CharBlock(required=False),
                                ),
                                (
                                    "display",
                                    wagtail.core.blocks.ChoiceBlock(
                                        choices=[
                                            ("", "Select a display ratio"),
                                            ("widescreen", "16:9"),
                                            ("fourbythree", "4:3"),
                                            ("audio", "Audio"),
                                            ("panorama", "Panorama"),
                                            ("square", "Square"),
                                            ("vertical", "Vertical"),
                                        ],
                                        required=False,
                                    ),
                                ),
                                (
                                    "embed_block",
                                    wagtail.embeds.blocks.EmbedBlock(
                                        help_text="Insert an embed URL", icon="media"
                                    ),
                                ),
                            ],
                            icon="media",
                        ),
                    ),
                    ("table", wagtail.contrib.table_block.blocks.TableBlock()),
                    (
                        "two_column_section",
                        wagtail.core.blocks.ListBlock(
                            wagtail.core.blocks.StructBlock(
                                [
                                    (
                                        "heading",
                                        autharch_sharc.editor.models.stream_blocks.RichTextNoParagraphBlock(
                                            form_classname="column-heading"
                                        ),
                                    ),
                                    (
                                        "subheading",
                                        autharch_sharc.editor.models.stream_blocks.RichTextNoParagraphBlock(
                                            form_classname="column-subheading",
                                            required=False,
                                        ),
                                    ),
                                    (
                                        "body",
                                        autharch_sharc.editor.models.stream_blocks.APIRichTextBlock(
                                            form_classname="column-body"
                                        ),
                                    ),
                                ]
                            ),
                            form_classname="two-column-50-50",
                        ),
                    ),
                ]
            ),
        ),
        migrations.CreateModel(
            name="WagtailEADSnippet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("unittitle", models.TextField(blank=True, null=True)),
                ("reference", models.CharField(blank=True, max_length=256, null=True)),
                (
                    "ead",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="ead_snippets",
                        to="ead.EAD",
                    ),
                ),
            ],
            bases=(wagtail.search.index.Indexed, models.Model),
        ),
    ]