from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def resaltar_texto(value):
    new_value = f'<strong>{value}</strong>'
    # usamos mark_safe() para ejecutar el codigo html en lugar de solo leerlo como una variable string
    return mark_safe(new_value)

@register.filter
def formato_duracion(minutos):

    if minutos:
        minutos = int(minutos)
        horas = minutos // 60
        minutos_restantes = (minutos % 60)
        if minutos_restantes < 10:
            minutos_restantes = f"0{str(minutos_restantes)}"
    else:
        horas = None
        minutos_restantes = None
    return '{}:{} horas'.format(horas, minutos_restantes)