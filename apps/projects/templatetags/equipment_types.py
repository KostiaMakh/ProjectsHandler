from django import template

from config.constants import EQUIPMENT_TYPES

register = template.Library()


@register.simple_tag()
def get_equipment_name(val):
    for equipment_type in EQUIPMENT_TYPES:
        if val == equipment_type[0]:
            return equipment_type[1]

    return val


@register.simple_tag()
def multiple(a, b):
    return a * b
