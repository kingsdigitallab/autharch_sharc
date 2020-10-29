from django import template


register = template.Library()


@register.inclusion_tag('editor/includes/form_facet.html')
def render_facet(facet):
    """Renders the facet `facet`.

    `facet` is a Haystack facet, consisting of four items: the string
    display value, the integer count,.the string link to apply/unapply
    the facet, and a Boolean indicating whether the facet is selected.

    """
    context = {
        'count': facet[1],
        'label': facet[0],
        'link': facet[2],
        'selected': facet[3],
    }
    return context


@register.inclusion_tag('editor/includes/form_field.html')
def render_field(form_field):
    """Renders the form field `form_field`, including label, widget, and
    error messages."""
    if isinstance(form_field, str):
        return {}
    attrs = form_field.field.widget.attrs
    if form_field.errors:
        attrs['class'] = ' '.join(
            (attrs.get('class', ''), form_field.css_classes(), 'error'))
    widget = form_field.as_widget(attrs=attrs)
    return {
        'errors': form_field.errors,
        'help_text': form_field.help_text,
        'is_hidden': form_field.is_hidden,
        'label': form_field.label,
        'required': form_field.field.required,
        'widget': widget,
    }


@register.inclusion_tag('editor/includes/delete_form_field.html')
def render_form_delete_widget(field):
    """Renders the widget for a form's DELETE `field`."""
    if isinstance(field, str):
        return {}
    context = {}
    context['widget'] = field.as_widget(
        attrs={'aria-label': 'delete field checkbox'})
    return context
