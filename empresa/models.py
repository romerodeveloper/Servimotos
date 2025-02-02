from django.db import models
from django.forms import model_to_dict

class Empresa(models.Model):
    razonSocial = models.CharField(max_length=255, verbose_name='Razon Social', unique=True, null=False, default="Sin definir")
    nit = models.IntegerField(verbose_name='Nit', unique=True, null=False, default=000000)
    telefonoPrincipal = models.IntegerField(verbose_name='Telefono Principal de Empresa', null=False, max_length=12, default=0000000000)
    correo = models.CharField(max_length=255, verbose_name='Correo Electronico', null=True)
    nombreRepresentante = models.CharField(max_length=255, verbose_name='Nombre Representante', null=False, default="Sin definir")

    class Meta:
        abstract = True