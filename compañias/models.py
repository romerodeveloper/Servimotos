from django.db import models

from empresa.models import Empresa


class Compañia(Empresa):
    ventasTotales = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Ventas totales de la compañia')
    comprasTotales = models.DecimalField(max_digits=12, decimal_places=0, verbose_name='Compras totales de la compañia')

    def toJSON(self):
        item = super().toJSON()
        return item

    def __str__(self):
        return self.razonSocial