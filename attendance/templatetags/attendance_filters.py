from django import template

register = template.Library()


@register.filter
def dict_get(dictionary, key):
    """Get value from dictionary by key. Usage: dict|dict_get:key"""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None


@register.filter
def first_or_default(value, default=""):
    """Get first element or return default. Usage: list|first_or_default:"default" """
    if value:
        return value[0] if isinstance(value, (list, tuple)) else value
    return default


@register.filter
def mul(value, arg):
    """Multiply value by arg. Usage: value|mul:2"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def div(value, arg):
    """Divide value by arg. Usage: value|div:2"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

