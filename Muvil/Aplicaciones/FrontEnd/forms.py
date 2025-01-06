from django import forms
from django.forms import ModelForm, TextInput, ChoiceField, RadioSelect, DateInput, NumberInput, Textarea, TimeInput, \
    Select, CheckboxInput
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, PasswordResetForm
from ..users.admin import UserCreationForm as CustomUserCreationForm
from .models import Personas, Viajes, Vehiculos, Opiniones, Usuario, Caparazones
from .choices import genero, tipo_vehiculo, prestigio, categorias_puntuacion, modelos, equipaje, documentos_identidad
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from datetime import datetime
from ..users.models import Usuario

class PersonasForm(ModelForm):
    class Meta:
        model = Personas
        fields = ('nombre', 'apellido1','apellido2','tipo_documento','numero_documento','fec_nacimiento',
                  'num_telefono','descripcion','imagen')

        fec_nacimiento = forms.DateField(
            required=True,
            input_formats=(
                '%Y-%m-%d',  # '2006-10-25'
                '%d-%m-%Y',  # '25-10-2006'
                '%m/%d/%Y',  # '10/25/2006'
                '%m/%d/%y'
            )
        )  # '10/25/06')

        widgets = {
            'fec_nacimiento': DateInput(attrs={
                'class': "form-control",
            }),
            'nombre': TextInput(attrs={
                'class': "form-control",
                'minlength': 3,
            }),
            'apellido1': TextInput(attrs={
                'class': "form-control",
                'minlength': 3,
            }),
            'apellido2': TextInput(attrs={
                'class': "form-control",
            }),
            'tipo_documento': Select(
                attrs={
                    'class': "form-select",
                },
                choices=documentos_identidad,
            ),
            'numero_documento': TextInput(attrs={
                'class': "form-control",
                'pattern':".{9}", # 9 caracteres
            }),
            'num_telefono': TextInput(attrs={
                'class': "form-control",
            }),
            'descripcion': Textarea(attrs={
                'class': "form-control",
                'rows': '3',
                'placeholder': 'Descríbete en pocas palabras y encuentra gente como tú...'
            }),
            'password': TextInput(attrs={
                'class': "form-control",
            })
        }

class CaparazonesForm(ModelForm):
    class Meta:
        model = Caparazones
        fields = ('idiomas', 'profesion', 'aficiones', 'estilo_musica', 'grupos_musica', 'libros', 'peliculas',
                  'deportes', 'alimentacion', 'animales')

        widgets = {
            'idiomas': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Español, Inglés, Portugués, ..."
            }),
            'profesion': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Enfermería/Profesora de primaria/Ingeniero de Teleco ..."
            }),
            'aficiones': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Videojuegos, el Vino, salir de Fiesta, ..."
            }),
            'estilo_musica': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Reggaeton, Trap, Techno, ..."
            }),
            'grupos_musica': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Marc Anthony, Estopa, ColdPlay, ..."
            }),
            'libros': TextInput(attrs={
                'class': "form-control",
                'placeholder': "El principito, Don Quijote de la Mancha, El poder del Ahora, ..."
            }),
            'peliculas': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Juego de Tronos, El lobo de Wall Street, Kill Bill, ..."
            }),
            'deportes': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Baloncesto, Fútbol, Pádel, ..."
            }),
            'alimentacion': TextInput(attrs={
                'class': "form-control",
                'placeholder': "Veganismo/Vegetarianismo/Alimentación Emocional/..."
            }),
            'animales': TextInput(attrs={
                'class': "form-control",
                'placeholder':"3 perros, 2 gatos, 1 tortuga, ..."
            })
        }

class ViajesForm(ModelForm):
    class Meta:
        model = Viajes
        fields = ('ciudad_origen','ciudad_destino', 'punto_recogida', 'punto_destino', 'fecha_ida','hora_ida', 'flg_ida_vuelta', 'flg_confirmacion_auto',
                  'numero_asientos_viaje', 'importe_conductor_asiento', 'id_vehiculo', 'equipaje', 'detalles')
        FLG_IDA_VUELTA_CHOICES = [
            (True, 'Sí'),
            (False, 'No'),
        ]
        widgets = {
            'ciudad_origen': TextInput(attrs={
                'class': "form-control",
                'list': "localizaciones",
                'id': "ciudad_origen",
                'autocomplete': "off"
            }),
            'ciudad_destino': TextInput(attrs={
                'class': "form-control",
                'list': "localizaciones",
                'id': "ciudad_destino",
                'autocomplete': "off"
            }),
            'punto_recogida': TextInput(attrs={
                'class': "form-control",
                'id': "punto_recogida"
            }),
            'punto_destino': TextInput(attrs={
                'class': "form-control",
                'id': "punto_destino"
            }),
            'fecha_ida': DateInput(attrs={
                'class': "form-control",
                'type': 'date',
                'value': datetime.now().strftime("%Y-%m-%d")
            }),
            'hora_ida': TimeInput(attrs={
                'class': "form-control",
                'type': 'time',
                'list': 'lista_horas_viaje'
            }),
            'numero_asientos_viaje': NumberInput(attrs={
                'class': "form-control",
                'id': "numero_asientos_viaje"
            }),
            'importe_conductor_asiento': NumberInput(attrs={
                'class': "form-control",
                'step': 0.5,
                'id': "importe_conductor_asiento"
            }),
            'id_vehiculo': Select(attrs={
                'class': "form-select",
                'required': 'True',
            }),
            'flg_ida_vuelta': RadioSelect(choices=[
                (True, 'Sí'),
                (False, 'No')
            ], attrs={
                'id': "vuelta-radio"
            }),
            'flg_confirmacion_auto': CheckboxInput(attrs={
                'class': "form-check-input",
                'type': "checkbox"
            }),
            'equipaje': Select(
                attrs={
                    'class': "form-select",
                },
                choices=equipaje,
            ),
            'detalles': Textarea(attrs={
                'class': "form-control",
                'rows': '1',
                'placeholder': 'Otros detalles del viaje...'
            })
        }

    # Para mostrar solo los coches de ese usuario.
    # Ahora se añade al formulario ViajesForm el parametro user cada vez que se le llame
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ViajesForm, self).__init__(*args, **kwargs)
        self.fields['id_vehiculo'].queryset = Vehiculos.objects.filter(id_persona = Personas.objects.get(id_usuario = user.id))

class VueltaViajesForm(forms.Form):
    ciudad_origen_vuelta = forms.CharField(
        label='Ciudad Origen Vuelta',
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': 'campo_vuelta1',
            'autocomplete': 'off'
        })
    )
    ciudad_destino_vuelta = forms.CharField(
        label='Ciudad Destino Vuelta',
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': 'campo_vuelta2',
            'autocomplete': 'off'
        })
    )
    punto_recogida_vuelta = forms.CharField(
        label='Punto Recogida Vuelta',
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': "punto_recogida_vuelta"
        })
    )
    punto_destino_vuelta = forms.CharField(
        label='Punto Destino Vuelta',
        required=False,
        widget=forms.TextInput(attrs={
            'class': "form-control",
            'id': "punto_destino_vuelta"
        }),
    )
    fecha_vuelta = forms.DateField(
        label='Fecha Vuelta',
        required=False,
        widget=forms.DateInput(attrs={
            'class': "form-control",
            'type': 'date',
            'id': 'campo_vuelta3'
            }
        )
    )
    hora_vuelta = forms.TimeField(
        label='Hora Vuelta',
        required=False,
        widget=forms.TimeInput(attrs={
            'class': "form-control",
            'type': 'time',
            'list': 'lista_horas_viaje',
            'id': 'campo_vuelta4'
            }
        )
    )
    numero_asientos_vuelta = forms.IntegerField(
        label='Plazas Vuelta',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'id': 'campo_vuelta5'
            }
        )
    )
    importe_conductor_asiento_vuelta = forms.DecimalField(
        label='Precio Vuelta',
        required=False,
        widget=forms.NumberInput(attrs={
            'class': "form-control",
            'step': 0.5,
            'id': 'campo_vuelta6'
            }
        )
    )

class VehiculosForm(ModelForm):

    class Meta:
        model = Vehiculos
        fields = ('tipo_vehiculo','marca','modelo','color','anyo_antiguedad','numero_asientos','matricula',
                  'imagen_vehiculo')

        widgets = {
            'tipo_vehiculo': Select(
                attrs={
                    'class': "form-select"
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
        fields = ('puntuacion','mensaje_opinion')

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
                'placeholder': '¿Como ha sido tu experiencia?'
            })
        }

class ContactoForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    asunto = forms.CharField(label="Asunto", required=True)
    mensaje = forms.CharField(widget=forms.Textarea, required=True)

class LoginnForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    contrasenya = forms.CharField(label="Contraseña", required=True)

class CambiarPassForm(SetPasswordForm):
    class Meta:
        model = get_user_model()
        fields = ['new_password1', 'new_password2']

class ResetearPassForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(ResetearPassForm, self).__init__(*args, **kwargs)

    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class RegistrarUsuarioForm(CustomUserCreationForm):
    email = forms.EmailField(
        help_text='Una dirección de correo válida.',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control mb-2'})
    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'password1', 'password2']

    #captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

class ImportExportForm(forms.Form):
    #modelo = forms.CharField(label="Modelo", required=True)
    modelo = forms.ChoiceField(choices=modelos)
    fichero_import = forms.FileField(label="Fichero")
