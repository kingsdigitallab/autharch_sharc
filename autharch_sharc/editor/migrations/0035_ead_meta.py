# Generated by Django 3.0.10 on 2021-06-08 09:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("editor", "0034_move_ead_story"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="wagtaileadsnippet",
            options={
                "verbose_name": "EAD wagtail object",
                "verbose_name_plural": "EAD wagtail objects",
            },
        ),
    ]