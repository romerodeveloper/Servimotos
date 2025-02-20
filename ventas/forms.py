from django.forms import *
from datetime import datetime

from django.template.context_processors import request

from sociosMinoristas.models import SocioMinorista
from ventas.models import Venta


class VentaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['autocomplete'] = 'off'

        compania = self.request.user.sedePerteneciente.companiaPerteneciente.id
        self.fields['cliente'].queryset = SocioMinorista.objects.filter(compañiasAsociadas=compania)

    class Meta:
        model = Venta
        fields = '__all__'
        exclude = ['use']
        widgets = {
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
            'cliente': Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%'
            }),
            'estadoVenta': Select(attrs={
                'class': 'form-control select2',
                'style': 'width: 100%'
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
