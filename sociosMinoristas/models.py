from django.db import models

from compañias.models import Compañia
from empresa.models import Empresa


class SocioMinorista(Empresa):
    montoPendiente = models.FloatField(verbose_name='Dinero Pendiente', default=0)
    totalVentas = models.FloatField(verbose_name='Total de Ventas Realizadas', default=0)
    porcentajeDescuento = models.IntegerField(verbose_name='Descuento Fijo en Ventas', default=10)
    compañiasAsociadas = models.ManyToManyField(Compañia,
                                                related_name='socios_minoristas',
                                                blank=True)

    def toJSON(self):
        item = super().toJSON()
        item['montoPendiente'] = format(self.montoPendiente, '.2f')
        item['totalVentas'] = format(self.totalVentas, '.2f')
        return item

    def __str__(self):
        return f'{self.montoPendiente}'
