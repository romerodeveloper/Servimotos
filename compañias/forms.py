from django.forms import ModelForm, TextInput
from .models import Compañia


class CompañiaForm(ModelForm):
    class Meta:
        model = Compañia
        exclude = ['totalCompras']
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