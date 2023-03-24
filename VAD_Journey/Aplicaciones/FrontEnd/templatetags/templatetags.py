from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def resaltar_texto(value):
    new_value = f'<strong>{value}</strong>'
    # usamos mark_safe() para ejecutar el codigo html en lugar de solo leerlo como una variable string
    return mark_safe(new_value)
