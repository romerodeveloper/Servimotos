from django.forms import ModelForm, TextInput, Textarea

from marcas.models import Marca


class MarcaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control'
            form.field.widget.attrs['autocomplete'] = 'off'

    def clean(self):
        cleaned_data = super().clean()

        for field in self.fields:
            value = cleaned_data.get(field)
            if value and isinstance(value, str):
                cleaned_data[field] = value.upper()
        return cleaned_data

    class Meta:
        model = Marca
        fields = '__all__'
        exclude = ['compañiaAsociada']

