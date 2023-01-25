from django.forms import ModelForm, TextInput, Textarea

from categorias.models import Categoria


class CategoriaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Categoria
        fields = '__all__'
        widgets = {
            'nombre': TextInput(
                attrs={
                    'placeholder': 'Ingrese un nombre a nivel general'
                }
            ),
            'descripcion': Textarea(
                attrs={
                    'placeholder': 'Descripcion detallada de la categoria',
                    'rows':3,
                    'cols': 3

                }
            )
        }

