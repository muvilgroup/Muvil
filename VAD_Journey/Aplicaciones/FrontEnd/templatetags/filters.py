import django_filters
from django.forms import CheckboxInput, DateInput, DateTimeInput
from django.db import models
from ..models import Viajes

class ViajesFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name='fechor_ida',
                            widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                            lookup_expr='gt', label='Viajes desde:')
    fecha_hasta = django_filters.DateFilter(field_name='fechor_ida',
                          widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                          lookup_expr='lt', label='Viajes hasta')
    ciudad_origen = django_filters.CharFilter(field_name='ciudad_origen', label='Ciudad de Salida', lookup_expr='icontains')
    ciudad_destino = django_filters.CharFilter(field_name='ciudad_destino', label='Ciudad de Destino', lookup_expr='icontains')

    class Meta:
        model = Viajes
        fields = ['fecha_desde', 'fecha_hasta','ciudad_origen','ciudad_destino','flg_solicitado',
                  'flg_reservado','flg_cancelado']
        '''
        filter_overrides = {
            models.CharField: {
                'filter_class': django_filters.CharFilter,
                'extra': lambda f: {
                    'lookup_expr': 'icontains',
                },
            },
            models.BooleanField: {
                'filter_class': django_filters.BooleanFilter,
                'extra': lambda f: {
                    'widget': CheckboxInput,
                },
            }'   
        }'''


