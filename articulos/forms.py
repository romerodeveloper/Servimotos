from django.forms import ModelForm, TextInput, Textarea

from articulos.models import Articulo
from categorias.models import Categoria
from distribuidores.models import Distribuidor
from marcas.models import Marca


class ArticuloForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            compania_id = self.user.sedePerteneciente.companiaPerteneciente.id
            self.fields['distribuidor'].queryset = Distribuidor.objects.filter(compañiaAsociada_id=compania_id)
            self.fields['marca'].queryset = Marca.objects.filter(compañiaAsociada_id=compania_id)
            self.fields['categoria'].queryset = Categoria.objects.filter(compañiaAsociada_id=compania_id)

        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Articulo
        exclude = ['sede']
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
