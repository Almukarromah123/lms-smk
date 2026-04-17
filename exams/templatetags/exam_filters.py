from django import template

register = template.Library()


@register.filter(name='get_dict_value')
def get_dict_value(dictionary, key):
    """Get value from dictionary by key (handles UUID keys)"""
    if dictionary is None:
        return None
    # Try direct key first
    if key in dictionary:
        return dictionary[key]
    # Try string version of key  
    if str(key) in dictionary:
        return dictionary[str(key)]
    return None
