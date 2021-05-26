from wagtail.core import blocks
from wagtail.core.rich_text import expand_db_html


class APIRichTextBlock(blocks.RichTextBlock):
    """
    Rich text parsed block to get internal links
    From https://github.com/wagtail/wagtail/issues/2695
    """

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        return expand_db_html(representation)
