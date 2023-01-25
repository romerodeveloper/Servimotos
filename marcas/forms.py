from django.forms import ModelForm, TextInput, Textarea

from marcas.models import Marca


class MarcaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'
    class Meta:
        model = Marca
        fields = '__all__'

