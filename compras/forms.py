from django.forms import *
from datetime import datetime
from ventas.models import Venta

from compras.models import Compra


class CompraForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        # forma 1
        self.fields['distribuidor'].widget.attrs['autofocus'] = True
        self.fields['distribuidor'].widget.attrs['class'] = 'form-control select2'
        self.fields['distribuidor'].widget.attrs['style'] = 'width: 100%'

        # forma 2
        # self.fields['cli'].widget.attrs = {
        #     'autofocus': True,
        #     'class': 'form-control select2',
        #     'style': 'width: 100%'
        # }

    class Meta:
        model = Compra
        fields = '__all__'
        widgets = {
            'distribuidor': Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%'
            }),
            'date_joined': DateInput(
                format='%Y-%m-%d',
                attrs={
                    'value': datetime.now().strftime('%Y-%m-%d'),
                    'autocomplete': 'off',
                    'class': 'datetimepicker-input form-control',
                    'id': 'date_joined',
                    'data-target': '#date_joined',
                    'data-toggle': 'datetimepicker'
                }
            ),
            'iva': TextInput(attrs={
                'class': 'form-control',
            }),
            'descuento': TextInput(attrs={
                'class': 'form-control',
                'id': 'desc'
            }),
            'subtotal': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
            }),
            'total': TextInput(attrs={
                'readonly': True,
                'class': 'form-control',
            })
        }