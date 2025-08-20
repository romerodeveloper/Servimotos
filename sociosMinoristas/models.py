from django.db import models

from compañias.models import Compañia
from empresa.models import Empresa


class SocioMinorista(Empresa):
    class PrestamoChoices(models.TextChoices):
        ACTIVO = "ACTIVO"
        INACTIVO = "INACTIVO"

    prestamo = models.CharField(
        max_length=10,
        choices=PrestamoChoices.choices,
        default=PrestamoChoices.INACTIVO,
        verbose_name="Estado del Préstamo"
    )

    montoMaximoPendiente = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Cupo maximo de prestamo', default= 0)
    montoPendiente = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Dinero Pendiente', default=0)
    totalVentas = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Total de Ventas Realizadas', default=0)
    porcentajeDescuento = models.IntegerField(verbose_name='Descuento Fijo en Ventas', default=10)
    compañiasAsociadas = models.ManyToManyField(Compañia,
                                                related_name='socios_minoristas',
                                                blank=True)

    def toJSON(self):
        item = super().toJSON()
        item['razonSocial'] = self.razonSocial
        item['montoPendiente'] = self.montoPendiente
        item['totalVentas'] = self.totalVentas
        item['montoMaximoPendiente'] = self.montoMaximoPendiente
        return item

    def __str__(self):
        return f'{self.razonSocial}'
