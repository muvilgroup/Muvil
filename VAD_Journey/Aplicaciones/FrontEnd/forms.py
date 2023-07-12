from django import forms
from django.forms import ModelForm, TextInput, EmailInput, RadioSelect, DateInput, NumberInput, Textarea, TimeInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from ..users.admin import UserCreationForm as CustomUserCreationForm
from .models import Personas, Viajes, Vehiculos, Opiniones, Usuario
from .choices import genero, tipo_vehiculo, prestigio, categorias_puntuacion, modelos
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox

class PersonasForm(ModelForm):

    class Meta:
        model = Personas
        fields = ('nombre', 'apellido1','apellido2','tipo_documento','numero_documento','fec_nacimiento',
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
            ''''password': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),
            'email': EmailInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;'
            }),'''
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
                'type': 'date',
                'format': '%d-%m-%Y',
                'style': 'max-width: 300px;'
            }),
            'numero_telefono': NumberInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'max': '999999999'
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
                'style': 'max-width: 300px;',
                'list': "localizaciones"
            }),
            'ciudad_destino': TextInput(attrs={
                'class': "form-control",
                'style': 'max-width: 300px;',
                'list': "localizaciones"
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
                choices=categorias_puntuacion,
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

class ContactoForm(forms.Form):
    email = forms.CharField(label="Email", required=True)
    asunto = forms.CharField(label="Asunto", required=True)
    mensaje = forms.CharField(widget=forms.Textarea, required=True)

class CambiarPassForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

class ResetearPassForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(ResetearPassForm, self).__init__(*args, **kwargs)

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class RegistrarUsuarioForm(CustomUserCreationForm):
    email = forms.EmailField(help_text='A valid email address, please.', required=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2']

    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class ImportExportForm(forms.Form):
    #modelo = forms.CharField(label="Modelo", required=True)
    modelo = forms.ChoiceField(choices=modelos)
    fichero_import = forms.FileField(label="Fichero")
