from django.db import models
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
    compañiaAsociada = models.ForeignKey(
        'compañias.Compañia',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def toJSON(self):
        item = super().toJSON() if hasattr(super(), 'toJSON') else {}
        item['totalCompras'] = format(self.totalCompras if self.totalCompras is not None else 0, '.2f')
        item['modeloFactura'] = self.get_modeloFactura_display()
        return item

    def __str__(self):
        return f'{self.razonSocial}'