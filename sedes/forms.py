from django.forms import ModelForm, TextInput

from sedes.models import Sede


class SedeForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Sede
        fields = '__all__'
        exclude = ['ventasTotales', 'comprasTotales', 'companiaPerteneciente']
        widgets = {
            'direccion': TextInput(
                attrs={
                    'placeholder': 'Ingrese direccion de la sede',
                }
            )
        }
