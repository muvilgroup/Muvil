import django_filters
from django.forms import CheckboxInput, DateInput, DateTimeInput, MultipleChoiceField, Select, TextInput, NumberInput, RadioSelect
from django.db import models
from ..models import Viajes, Mensajes
from ..choices import estados_viajes, categorias_puntuacion


class MisViajesFilter(django_filters.FilterSet):
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
        label="Estado",
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

class BuscarViajeFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name='fechor_ida',
                            widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                            lookup_expr='gt', label='Viajes desde:')
    fecha_hasta = django_filters.DateFilter(field_name='fechor_ida',
                          widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                          lookup_expr='lt', label='Viajes hasta')

    precio_desde = django_filters.NumberFilter(field_name='importe_total_asiento',
                                            widget=NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
                                            lookup_expr='gte', label='Precio desde:')
    precio_hasta = django_filters.NumberFilter(field_name='importe_total_asiento',
                                            widget=NumberInput(attrs={'class': 'form-control', 'type': 'number'}),
                                            lookup_expr='lte', label='Precio hasta:')

    categoria_minima = django_filters.ChoiceFilter(
        field_name='id_persona__puntuacion',
        choices=categorias_puntuacion,
        label="Puntuación mínima:",
        empty_label="Todas las puntuaciones",
        widget=Select(attrs={'class': 'form-control'}),
        lookup_expr='gte'
    )


    estado = django_filters.ChoiceFilter(
        choices = estados_viajes,
        empty_label="Todos los estados",
        label="Estado",
        widget=Select(attrs={'class': 'form-control'})
        )

    class Meta:
        model = Viajes
        fields = ['fecha_desde', 'fecha_hasta', 'precio_desde', 'precio_hasta','categoria_minima']


class UsuarioviajesopinionesFilter(django_filters.FilterSet):
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
        field_name='estado',
        choices = estados_viajes,
        label="Estado",
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


class MensajesFilter(django_filters.FilterSet):
    fecha_desde = django_filters.DateFilter(field_name='fec_created',
                            widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                            lookup_expr='gt', label='Mensajes desde:')
    fecha_hasta = django_filters.DateFilter(field_name='fec_created',
                          widget=DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                          lookup_expr='lt', label='Mensajes hasta')

    class Meta:
        model = Mensajes
        fields = ['fecha_desde', 'fecha_hasta']
