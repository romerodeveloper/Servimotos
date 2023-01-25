from django.db import models

# Create your models here.
from django.forms import model_to_dict


class Distribuidor(models.Model):
    razonSocial = models.CharField(max_length=255, verbose_name='Razon Social', unique=True)
    nit = models.CharField(max_length=255, verbose_name='Nit', unique=True)
    telefono = models.CharField(max_length=255, verbose_name='Telefono', unique=True)
    correo = models.CharField(max_length=255, verbose_name='Correo', unique=True)
    descripcion = models.CharField(max_length=255, verbose_name='Descripción')

    def toJSON(self):
        item = model_to_dict(self)
        return item

    def __str__(self):
        return f'{self.razonSocial}'