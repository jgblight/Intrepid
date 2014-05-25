from django import template

register = template.Library()

@register.inclusion_tag("field.html")
def field(field):
    return {'field':field,
    		'div_class':"form-group"}


@register.inclusion_tag("field.html")
def field_inline(field):
    return {'field':field,
    		'div_class':"inline-group"}