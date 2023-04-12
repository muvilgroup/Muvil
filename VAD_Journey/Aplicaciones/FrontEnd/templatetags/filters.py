import django_filters
from django.forms import CheckboxInput, DateInput, DateTimeInput, MultipleChoiceField, Select, TextInput
from django.db import models
from ..models import Viajes
from ..choices import estados_viajes


class ViajesFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name='fechor_ida',
                            widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                            lookup_expr='gt', label='Viajes desde:')
    fecha_hasta = django_filters.DateFilter(field_name='fechor_ida',
                          widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                          lookup_expr='lt', label='Viajes hasta')
    ciudad_origen = django_filters.CharFilter(field_name='ciudad_origen', label='Ciudad de Salida', lookup_expr='icontains',
                                              widget=TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    ciudad_destino = django_filters.CharFilter(field_name='ciudad_destino', label='Ciudad de Destino', lookup_expr='icontains',
                                               widget=TextInput(attrs={'class': 'form-control', 'type': 'text'}))
    estado = django_filters.ChoiceFilter(
        choices = estados_viajes,
        empty_label="Todos los estados",
        widget=Select(attrs={'class': 'form-control'})
        )

    class Meta:
        model = Viajes
        fields = ['fecha_desde', 'fecha_hasta','ciudad_origen','ciudad_destino','estado']
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


