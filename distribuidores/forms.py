from django.forms import ModelForm, TextInput, Textarea, HiddenInput

from distribuidores.models import Distribuidor


class DistribuidorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Distribuidor
        exclude = ['totalCompras']
        fields = '__all__'
        widgets = {
            'razonSocial': TextInput(
            attrs={
                'placeholder': 'Ingrese nombre del distribuidor',
            }
        ),
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
            'placeholder': 'Nombre de representate o Asesor',
        })
        }

