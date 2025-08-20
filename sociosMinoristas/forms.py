from django.forms import ModelForm, TextInput

from sociosMinoristas.models import SocioMinorista


class SocioForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

        self.fields['razonSocial'].initial = ''
        self.fields['nit'].initial = ''
        self.fields['telefonoPrincipal'].initial = ''
        self.fields['nombreRepresentante'].initial = ''

    def clean(self):
        cleaned_data = super().clean()

        for field in self.fields:
            if field != 'modeloFactura':
                value = cleaned_data.get(field)
                if value and isinstance(value, str):
                    cleaned_data[field] = value.upper()

        return cleaned_data


    class Meta:
        model = SocioMinorista
        fields = '__all__'
        exclude = ['totalVentas', 'montoPendiente', 'compañiasAsociadas']
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
            'correo': TextInput(attrs={
                'placeholder': 'Correo electrónico',
            }),
            'nombreRepresentante': TextInput(attrs={
                'placeholder': 'Nombre de representate o Asesor',
            }),
            'porcentajeDescuento': TextInput(attrs={
                'placeholder': 'Valor porcentual de descuento',
            }),
            'montoMaximoPendiente': TextInput(attrs={
                'placeholder': 'Valor maximo de prestamo',
            })
        }
