from django import template
from ..constants import ROUNDING_VALUE, HALF_STAR_VALUE
import math


register = template.Library()


@register.filter
def range_filter(value):
    if (value - int(value)) >= ROUNDING_VALUE:
        rounded_value = math.ceil(value)
    else:
        rounded_value = int(value)
    return range(rounded_value)


@register.filter
def has_half_star(value):
    return HALF_STAR_VALUE <= (value - int(value)) < ROUNDING_VALUE


@register.filter
def multiply(value, arg):
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''
