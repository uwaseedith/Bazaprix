from django import template
from Baza.utils import translate_text

register = template.Library()

@register.filter
def range_filter(value):
    return range(1, value + 1)

@register.filter(name='translate')
def translate(value, target_lang):
    """Translates text into the target language."""
    return translate_text(value, target_lang)
