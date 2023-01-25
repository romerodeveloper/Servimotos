from django.forms import ModelForm, TextInput, Textarea

from articulos.models import Articulo


class ArticuloForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Articulo
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre a nivel general',
                }
            ),
            'precioCosto': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Precio del distribuidor',
            }),
            'tasaGanacia': TextInput(attrs={
                'class': 'form-control',
                'id': 'tasa',
            }),
            'iva': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'placeholder': 'Precio calculado',
            }),
            'precioFinal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
                'placeholder': 'Precio calculado',
            }),
            'stock': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Unidades adquiridas'
            })

        }

