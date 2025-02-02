from django.db import models

from empresa.models import Empresa


class Compañia(Empresa):
    ventasTotales = models.FloatField(verbose_name='Ventas totales de la compañia')
    comprasTotales = models.FloatField(verbose_name='Compras totales de la compañia')

    def toJSON(self):
        item = super().toJSON()
        item['ventasTotales'] = format(self.ventasTotales, '.2f')
        item['comprasTotales'] = format(self.comprasTotales, '.2f')
        return item

    def __str__(self):
        return self.ventasTotales