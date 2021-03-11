from django import template

register = template.Library()

@register.simple_tag
def update_var(value):
    '''updates existing vars in template'''
    return value