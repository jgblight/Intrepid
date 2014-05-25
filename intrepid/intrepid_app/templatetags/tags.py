from django import template

register = template.Library()

@register.inclusion_tag("field.html")
def field(field):
    return {'field':field}