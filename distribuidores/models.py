from django.db import models

# Create your models here.
from django.forms import model_to_dict

from empresa.models import Empresa


class Distribuidor(Empresa):
    class ModeloFacturaChoices(models.TextChoices):
        IVA_CALCULADO = 'Calculado'
        IVA_NO_CALCULADO= 'No Calculado'
        IVA_EXENTO = 'Exento'
    telefonoAsesor = models.IntegerField(verbose_name='Telefono de Asesor', unique=True)
    totalCompras = models.FloatField(verbose_name='Total de Compras', default=0)
    modeloFactura = models.CharField(
        max_length=50,
        verbose_name='Modelo de Factura',
        choices=ModeloFacturaChoices.choices,
        default=ModeloFacturaChoices.IVA_NO_CALCULADO,
    )

    def toJSON(self):
        item = super().toJSON()
        item['totalCompras'] = format(self.totalCompras, '.2f')
        item['modeloFactura'] = self.get_modeloFactura_display()
        return item

    def __str__(self):
        return f'{self.razonSocial}'