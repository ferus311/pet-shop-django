# your_app/templatetags/custom_tags.py

from django import template
from django.urls import reverse
from django.utils.translation import gettext as _

register = template.Library()


@register.filter
def getattr_value(obj, field_name):
    """Lấy giá trị của trường đối tượng theo tên trường"""
    try:
        return getattr(obj, field_name, '')
    except AttributeError:
        return ''


@register.filter
def get_display_value(obj, field_name):
    """
    Get the display value for a field with choices.
    """
    if hasattr(obj, f'get_{field_name}_display'):
        return getattr(obj, f'get_{field_name}_display')()
    return getattr(obj, field_name, '')


@register.filter
def format_decimal(value):
    """
    Format a decimal value to two decimal places.
    """
    if value is not None:
        return f'{value:.2f}'
    return ''


@register.simple_tag
def admin_change_url(obj):
    return reverse(
        f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',
        args=[
            obj.pk])


@register.filter
def get_model_opts(instance):
    model = instance.__class__
    opts = model._meta
    return opts
