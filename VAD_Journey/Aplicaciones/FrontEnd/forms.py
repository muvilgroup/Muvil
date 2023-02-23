from django.forms import ModelForm, TextInput, EmailInput, RadioSelect, DateInput, NumberInput, Textarea, TimeInput
from .models import Personas, Viajes, Vehiculos, Opiniones
from .choices import genero, tipo_vehiculo, prestigio, categoria_puntuacion

class PersonasForm(ModelForm):

    class Meta:
        model = Personas
        fields = ('nombre', 'apellido1','apellido2','password','email','tipo_documento','numero_documento','fec_nacimiento',
                  'numero_telefono','descripcion','imagen')
        widgets = {
            'nombre': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'apellido1': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'apellido2': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'password': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'email': EmailInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'tipo_documento': RadioSelect(
                attrs={
                'class': "form-check-inline",
                },
                choices=[
                            ('DNI', 'DNI'),
                            ('NIE', 'NIE'),
                            ('PASSWORD', 'PASSWORD'),
                        ],
            ),
            'numero_documento': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'fec_nacimiento': DateInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'type': 'date'
            }),
            'numero_telefono': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'descripcion': Textarea(attrs={
                'class': "form-control",
                'rows': '3',
                'placeholder': 'Descríbete en pocas palabras y encuentra gente como tú...'
            }),
            'password': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            })
        }


class ViajesForm(ModelForm):

    class Meta:
        model = Viajes
        fields = ('ciudad_origen','ciudad_destino','flg_ida_vuelta','fecha_ida','fecha_vuelta','hora_ida','hora_vuelta',
                  'numero_asientos_viaje', 'importe_conductor_asiento')
        widgets = {
            'ciudad_origen': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'ciudad_destino': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'flg_ida_vuelta': RadioSelect(
                attrs={
                    'class': "form-check-inline",
                },
                choices=[
                    ('I', 'Ida'),
                    ('IV', 'Ida/Vuelta'),
                ],
            ),
            'fecha_ida': DateInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'type': 'date'
            }),
            'fecha_vuelta': DateInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'type': 'date'
            }),
            'hora_ida': TimeInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'type': 'time'
            }),
            'hora_vuelta': TimeInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'type': 'time'
            }),
            'numero_asientos_viaje': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'importe_conductor_asiento': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'step': 0.5
            })
        }


class VehiculosForm(ModelForm):

    class Meta:
        model = Vehiculos
        fields = ('tipo_vehiculo','marca','modelo','color','anyo_antiguedad','numero_asientos','matricula',
                  'imagen_vehiculo')

        widgets = {
            'tipo_vehiculo': RadioSelect(
                attrs={
                    'class': "form-check-inline",
                },
                choices=tipo_vehiculo,
            ),
            'marca': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'modelo': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'color': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'anyo_antiguedad': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'numero_asientos': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'matricula': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            })
        }

class OpinionesForm(ModelForm):

    class Meta:
        model = Opiniones
        fields = ('puntuacion','mensaje_opinion','mensaje_respuesta')

        widgets = {
            'puntuacion': RadioSelect(
                attrs={
                    'class': "form-check-inline",
                },
                choices=categoria_puntuacion,
            ),
            'mensaje_opinion': Textarea(attrs={
                'class': "form-control",
                'rows': '3',
                'placeholder': 'Descríbete en pocas palabras y encuentra gente como tú...'
            }),
            'mensaje_respuesta': Textarea(attrs={
                'class': "form-control",
                'rows': '3',
                'placeholder': 'Descríbete en pocas palabras y encuentra gente como tú...'
            })
        }
