from django.forms import ModelForm, TextInput, EmailInput, RadioSelect, DateInput, NumberInput, Textarea, ImageField
from .models import Personas

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