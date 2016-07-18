from django import template

register = template.Library()

@register.filter
def lookup(value, key):
    if type(value) is dict:
        return value.get(key, '')
    else:
        return ''
