from django.forms import ModelForm, TextInput, Textarea


from distribuidores.models import Distribuidor


class DistribuidorForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    class Meta:
        model = Distribuidor
        fields = '__all__'
        widgets = {
            'razonSocial': TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Ingrese nombre del distribuidor',
                }
            ),
            'nit': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nit sin guión',
            }),
            'telefono': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Celular o Fijo',
            }),'correo': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Correo electronico',
            }),
            'descripcion': Textarea(attrs={
                'class': 'form-control',
                "rows": 3, "cols": 12,
                'placeholder': 'Descripcion de los productos que abastece',
            }),

        }

