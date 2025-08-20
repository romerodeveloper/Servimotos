from django.forms import ModelForm, TextInput, Textarea, HiddenInput

from distribuidores.models import Distribuidor

from django import forms
from django.forms import ModelForm, TextInput
from .models import Distribuidor


class DistribuidorForm(ModelForm):
    class Meta:
        model = Distribuidor
        exclude = ['totalCompras', 'compañiaAsociada']
        widgets = {
            'razonSocial': TextInput(attrs={
                'placeholder': 'Ingrese nombre del distribuidor',
            }),
            'nit': TextInput(attrs={
                'placeholder': 'Nit sin guión',
            }),
            'telefonoPrincipal': TextInput(attrs={
                'placeholder': 'Celular o Fijo',
            }),
            'telefonoAsesor': TextInput(attrs={
                'placeholder': 'Celular o Fijo',
            }),
            'correo': TextInput(attrs={
                'placeholder': 'Correo electrónico',
            }),
            'nombreRepresentante': TextInput(attrs={
                'placeholder': 'Nombre de representante o Asesor',
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Aplicar clases y desactivar autocompletado
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['autocomplete'] = 'off'

        # Eliminar valores por defecto
        self.fields['razonSocial'].initial = ''
        self.fields['nit'].initial = ''
        self.fields['nombreRepresentante'].initial = ''
        self.fields['telefonoPrincipal'].initial = ''

    def clean(self):
        cleaned_data = super().clean()

        for field in self.fields:
            if field != 'modeloFactura':
                value = cleaned_data.get(field)
                if value and isinstance(value, str):
                    cleaned_data[field] = value.upper()

        return cleaned_data
