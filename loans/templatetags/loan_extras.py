from django import template

register = template.Library()

@register.filter
def neg(value):
    """Return negative value for display"""
    return -value